fout = open("dblp3.xml", "wt")
fin = open("dblp.xml", "rt")
for line in fin:
    line = line.replace('&', 'e')
    fout.write(line)
