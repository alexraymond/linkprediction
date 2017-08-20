import collections
from itertools import repeat, izip
import math
from random import sample, shuffle
import warnings


class DataEncoder(object):
    def __init__(self):
        raise NotImplementedError('This class is abstract. Derive it.')

    def __call__(self, observation):
        raise NotImplementedError('This method is abstract. Override it.')

    def unmap(self, addresses):
        raise NotImplementedError('This method is abstract. Override it.')


class BitStringEncoder(DataEncoder):
    '''A bit string to addresses list encoder.

    Based on a mapping randomly defined on the first map() call, maps the bits
    of a given bit string into a list of addresses which could, for example,
    be input to a WiSARD discriminator.

    Attributes:
        nmbr_neurons: the length of the addresses list to be generated.
        mapping: the mapping used to define the addresses.
        reverse_mapping: a mapping which could be used to retrieve the bit
            string used to produce an addresses list.
    '''

    def __init__(self, nmbr_neurons):
        self.nmbr_neurons = nmbr_neurons
        self.mapping = self.reverse_mapping = None

    def __call__(self, bit_string):
        '''Maps a bit string, according to a mapping.

        The mapping is randomly defined on the first call to this method.

        Returns:
            BitStringEncoder(2).map('11110001') would return, considering that
            mapping = [7, 6, 1, 5, 2, 4, 3, 0]:
                '11110001' ======== mapping ===========> '10101011',
                '10101011' ======== splitting =========> ['1010', '1011'],
                ['1010', '1011'] == making addresses ==> [10, 11].

            BitStringEncoder(2).map('11110001') = [10, 11]
        '''

        if self.nmbr_neurons == 1:
            return int(bit_string, 2)

        if not self.mapping:
            self.mapping = range(len(bit_string))
            shuffle(self.mapping)
        
        bits = ''.join(bit_string[x] for x in self.mapping)

        return [int(bits[i::self.nmbr_neurons], 2)
                for i in xrange(self.nmbr_neurons)]

    def unmap(self, addresses):
        if self.nmbr_neurons == 1:
            s = bin(addresses)[2:]
            return '0' * (len(self.mapping) - len(s)) + s

        min_addr_len = len(self.mapping) / self.nmbr_neurons
        plus_one_lim = len(self.mapping) % self.nmbr_neurons

        def plus_one_fix(a, i):
            if len(a) == min_addr_len + plus_one_lim:
                return a

            return '0' + a if i < plus_one_lim else a + '0'

        bits = ''.join(
                plus_one_fix(a.zfill(min_addr_len), i)
                     for i, a in enumerate(bin(a)[2:] for a in addresses))

        if plus_one_lim: min_addr_len += 1
        bits = ''.join(bits[i::min_addr_len] for i in xrange(min_addr_len))

        if not self.reverse_mapping:
            self.reverse_mapping = [0] * len(self.mapping)

            for i, j in enumerate(self.mapping):
                self.reverse_mapping[j] = i

        return ''.join(bits[x] for x in self.reverse_mapping)



