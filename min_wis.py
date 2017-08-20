from collections import defaultdict
from itertools import izip


class Neuron(object):
    '''The superclass of all WiSARD-like neurons.

    This should be used as a template to any neuron implementation, as an
    abstract class, but no method is indeed required to be overriden.
    '''

    def __init__(self):
        raise NotImplementedError('This class is abstract. Derive it.')

    def __len__(self):
        '''Returns how many RAM locations are written.'''
        raise NotImplementedError('This method is abstract. Override it.')

    def __iter__(self):
        '''Returns an iterator to the wirtten RAM locations.'''
        raise NotImplementedError('This method is abstract. Override it.')

    def record(self, address):
        '''Writes the location addressed by the given argument.'''
        raise NotImplementedError('This method is abstract. Override it.')

    def answer(self, address):
        '''Returns true iff the location being addressed is written.'''
        raise NotImplementedError('This method is abstract. Override it.')

    def count(self, address):
        '''Returns how many times the location being addressed was written.'''
        raise NotImplementedError('This method is abstract. Override it.')

    def bit_counts(self):
        '''Returns how many times each bit was set in the addresses recorded.

        This method return a list 'bit_freq', where bit_freq[i] is the number
        of times the bit i was set in the addresses recorded.

        '''
        raise NotImplementedError('This method is abstract. Override it.')

    def intersection_level(self, neuron):
        '''Returns the ammount of locations written in both neurons.

        Considering a & b the intersection of the locations written in both
        neurons and a | b their union, this method returns (a & b)/(a | b).
        '''
        raise NotImplementedError('This method is abstract. Override it.')

    def bleach(self, threshold):
        '''Bleach each location written.

        The bleach operation is described as to reduce the writing count of a
        location by the given threshold if this count is over the threshold. If
        not, this location is cleaned.
        '''
        raise NotImplementedError('This method is abstract. Override it.')

    def min_answer(self):
        '''Returns the lowest answer value the neuron gives.

        The default WiSARD neuron answers 0 or 1. However, there is no
        restriction to the answer a neurons gives other than being numeric.
        '''
        raise NotImplementedError('This method is abstract. Override it.')

    def max_answer(self):
        '''Returns the highest answer value the neuron gives.

        The default WiSARD neuron answers 0 or 1. However, there is no
        restriction to the answer a neurons gives other than being numeric.
        '''
        raise NotImplementedError('This method is abstract. Override it.')


class DictNeuron(Neuron):
    '''A basic neuron based on Python's dict(). PyWNN's default neuron.'''
    def __init__(self):
        self.locations = defaultdict(int)
        # defaultdict faster than Counter (Python 2.7.3, 2013/02/22)

    def __len__(self):
        return len(self.locations)

    def __iter__(self):
        return iter(self.locations)

    def record(self, address):
        self.locations[address] += 1

    def answer(self, address):
        return address in self.locations

    def count(self, address):
        return self.locations.get(address, 0)

    def bit_counts(self):
        bit_freq = [0]

        for addr, freq in self.locations.viewitems():
            while addr:
                last_bit_index = (addr & -addr).bit_length() - 1
                bit_freq.extend([0] * (last_bit_index + 1 - len(bit_freq)))
                bit_freq[last_bit_index] += freq
                addr &= addr - 1  # unset last bit

        return bit_freq

    def intersection_level(self, neuron):
        len_intrsctn = len(
            self.locations.viewkeys() & neuron.locations.viewkeys())
        len_union = len(
            self.locations.viewkeys() | neuron.locations.viewkeys())
        return len_intrsctn * 1. / len_union

    def bleach(self, threshold):
        for address in self.locations.keys():
            if self.locations[address] > threshold:
                self.locations[address] -= threshold
            else:
                del self.locations[address]


class Discriminator(object):
    '''The default WiSARD discriminator.'''

    def __init__(self, neuron_factory=DictNeuron):
        '''Inits a Discriminator with the given number of neurons.
        
        The type of neuron to be used can be specified through the neuron
        parameter. The argument must be callable, returning a neuron object.
        '''

        self.neurons = None
        self.neuron_factory = neuron_factory

    def __len__(self):
        return len(self.neurons)

    def range(self):
        '''Returns how many input patterns are totally known.'''
        return reduce(op.mul, (len(neuron) for neuron in self.neurons))

    def record(self, observation):
        '''Record the provided observation.

        The observation is expected to be a list of addresses, each of which
        will be recorded in its respective neuron.
        '''

        if self.neurons is None:
            self.neurons = [self.neuron_factory() for _ in observation]

        for address, neuron in izip(observation, self.neurons):
            neuron.record(address)

    def answer(self, observation):
        '''Returns how similar the observation is to the stored knowledge.

        The return value is the sum of the answers of each neuron to its
        respective address. This value can be normalized by being divided
        by the number of neurons.
        '''

        return sum(neuron.answer(address)
            for address, neuron in izip(observation, self.neurons))

    def counts(self, observation):
        '''Returns how many times the observation addresses were recorded.

        This method is intended to be used to compare discriminators
        answers using bleaching. This way, the counts are sorted
        what permits 'regular' comparisons (cmp(), <, and others).

        '''

        counts = (n.count(addr) for addr, n in izip(observation, self.neurons))
        return sorted(c for c in counts if c)

    def drasiw(self):
        '''Returns how many times each bit was set in the addresses recorded.

        This method return a list of lists 'drasiw', where drasiw[i][j] is
        the number of times the bit j was set in the addresses recorded
        by neuron i.

        '''
        return [neuron.bit_counts() for neuron in self.neurons]

    def intersection_level(self, dscrmntr):
        '''Returns the intersection level between the discriminators.

        This is calculated as the mean intersection level between the
        the n-th neurons of each discriminator, for every possible n.
        '''

        return mean(na.intersection_level(nb)
            for na, nb in izip(self.neurons, dscrmntr.neurons))

    def bleach(self, threshold):
        '''Bleach each discriminator neuron by the given threshold.'''

        for n in self.neurons:
            n.bleach(threshold)

    def min_answer(self):
        '''Returns the lowest answer value the discriminator gives.

        This method returns just the sum of the min_answer of the neurons.
        '''
        return sum(neuron.min_answer() for neuron in self.neurons)

    def max_answer(self):
        '''Returns the highest answer value the discriminator gives.

        This method returns just the sum of the max_answer of the neurons.
        '''
        return sum(neuron.max_answer() for neuron in self.neurons)


class WiSARDLikeClassifier(object):
    '''The superclass of all WiSARD-like classifiers.

    This should be used as a template to any classifier implementation, as an
    abstract class, but no method is indeed required to be overriden.
    '''

    def __init__(self):
        raise NotImplementedError('This class is abstract. Derive it.')

    def record(self, observation, class_):
        '''Record the provided observation, relating it to the given class.'''
        raise NotImplementedError('This method is abstract. Override it.')

    def answers(self, observation, class_=None):
        '''Returns how similar the observation is to the known classes.

        By default, a dictionary with the classes labels as keys and the
        respective similarities between observation and classes as values is
        returned.

        Parameters
            observation: the observation in which the answers must be based
            class_: if given, only the similarity wrt this class is returned
        '''

        raise NotImplementedError('This method is abstract. Override it.')

    def counts(self, observation, class_=None):
        '''Returns a description of observation similarity to known classes.

        The description of the similarity must take into account the number of
        times the observation addresses were previously recorded.
        
        By default, a dictionary with the classes labels as keys and theirs
        respective similarity descriptions as values is returned.

        Parameters
            observation: the observation in which the answers must be based
            class_: if given, only the answer wrt this class is returned
        '''

        raise NotImplementedError('This method is abstract. Override it.')

    def remove_class(self, class_):
        raise NotImplementedError('This method is abstract. Override it.')


class WiSARD(WiSARDLikeClassifier):
    def __init__(self, discriminator=Discriminator):
        '''Inits a WiSARD classifier using the provided arguments.

        Parameters
            discriminator: the discriminator which will be used to learn about
                each class to be presented. The argument must be callable,
                returning a Discriminator-like object.
        '''

        self.discriminators = defaultdict(discriminator)

    def record(self, observation, class_):
        self.discriminators[class_].record(observation)

    def answers(self, observation, class_=None):
        if class_ is not None:
            return self.discriminators[class_].answer(observation)

        return {class_: dscrmntr.answer(observation)
            for class_, dscrmntr in self.discriminators.viewitems()}

    def counts(self, observation, class_=None):
        if class_ is not None:
            return self.discriminators[class_].counts(observation)

        return {class_: dscrmntr.counts(observation)
            for class_, dscrmntr in self.discriminators.viewitems()}

    def bleach(self, threshold):
        for d in self.discriminators:
            self.discriminators[d].bleach(threshold)

    def remove_class(self, class_):
        del self.discriminators[class_]
