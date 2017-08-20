from graph_tool.all import *
import timeit, random, collections
from min_wis import WiSARD
from encoding import BitStringEncoder
import math
import time

def countweightedpaths(source, target, path, timetolive, pathcounter, lastyear):
  g = source.get_graph()
  vertexindexes = g.vertex_properties["index"]
  #print "\n\nOn vertex " + str(vertexindexes[source])
  if source == target:
    #print "Found it!"
    return pathcounter
  if timetolive < 1 and source != target:
    #print "Dead end!"
    return 0
  thispath = list(path)
  #thispath = path
  thispath.append(source)
  edgeages = g.edge_properties["age"]
  weight = 0
  for neighbour in source.all_neighbours():
    edgeweights = 0.0
    if neighbour == target and timetolive > 1:
      continue
    if neighbour not in thispath:
      for e in g.edge(source, neighbour, all_edges=True):
	#print "To: " + str(vertexindexes[e.target()])
	#print "Edge age: " + str(edgeages[e])
	edgeweights += 1.0 / (lastyear - edgeages[e] + 1.0)
	#print "Adding " + str(1.0 / (lastyear - edgeages[e] + 1.0))
      weight += countweightedpaths(neighbour, target, thispath, timetolive-1, pathcounter + edgeweights, lastyear)
  return weight

def props(cls):
  return [i for i in cls.__dict__.keys() if i[:1] != '_']

def verticesatdistance(graph, source, d, vertices):
  g = graph
  vertices.add(source)
  if d > 0:
    for neighbour in source.all_neighbours():
      if neighbour not in vertices:
	verticesatdistance(g, neighbour, d-1, vertices)


def evaluatemodifiedjaccard(graph, source, target, shortestdistance, d):
  total = 0.0
  #shortestdistance = shortest_distance(source.get_graph(), source, target)
  #print shortestdistance
  #if shortestdistance > maxdistance + 1:
  #  return 0
  sourcevertices = set()
  targetvertices = set()
  verticesatdistance(graph, source, shortestdistance, sourcevertices)
  verticesatdistance(graph, target, shortestdistance, targetvertices)
  intersection = len(sourcevertices.intersection(targetvertices))
  union = len(sourcevertices.union(targetvertices))
  #print intersection, union, float(intersection)/float(union)
  return float(intersection)/float(union)

def evaluatepair(source, target, shortestdistance, d, baseyear):
  i = 0
  value = 0.0
  powervalue = 0.0
  jaccard = evaluatemodifiedjaccard(graph, source, target, shortestdistance, d)
  for i in range(2, d+1):
    paths = countweightedpaths(source, target, list(), i, 0.0, baseyear)
    value += jaccard * paths
    #value += pow(jaccard, i) * pow(paths, i)
  return value#, powervalue

def evaluategraph(g, d, rank):
  vertexindexes = g.vertex_properties["index"]
  bestu = 0
  bestv = 0
  largestvalue = 0.0
  for u in range(0, g.num_vertices()-1):
    for v in range(u, g.num_vertices()):
      shortestdistance = shortest_distance(g, g.vertex(u), g.vertex(v))
      if shortestdistance > d or shortestdistance < 2:
	continue
      value = evaluatepair(g, g.vertex(u), g.vertex(v), shortestdistance, d, 2013)
      rank[value] = (vertexindexes[g.vertex(u)],vertexindexes[g.vertex(v)])
      #print "(" + str(u) + "," + str(v) + ") = " + str(value) + "(" + str(shortestdistance) + ")"

def mapfromindex(g):
  indexmap = {}
  vertexindexes = g.vertex_properties["index"]
  for v in range(0, g.num_vertices()):
    indexmap[vertexindexes[g.vertex(v)]] = v
  return indexmap

def testresults(rank, g):
  totaledges = g.num_edges()
  i = 0
  j = 0
  hit = 0
  randomhit = 0
  vertexindexes = g.vertex_properties["index"]
  indexmap = mapfromindex(g)
  #print "SAFETY TEST: " + str(g.edge(g.vertex(indexmap[3442]), g.vertex(indexmap[24748])))
  #print "SAFETY TEST: " + str(g.edge(g.vertex(indexmap[25988]), g.vertex(indexmap[47156])))
  keylist = rank.keys()
  keylist.sort()
  keylist.reverse()
  gcheck = load_graph("t2010-20125.xml.gz")
  existing = 0
  for k in keylist:
    #print "(" + str(rank[k][0]) + ", " + str(rank[k][1]) + ") = " + str(k)
    if i >= totaledges:
      break
    #print "edge(" + str(k[1][0]) + "," + str(k[1][1]) + "): " + str(g.edge(g.vertex(k[1][0]), g.vertex(k[1][1])))
    i+=1
    for e in gcheck.edge(g.vertex(rank[k][0]), g.vertex(rank[k][1]), all_edges=True):
	existing += 1
    if g.edge(g.vertex(rank[k][0]), g.vertex(rank[k][1])) is not None:
	hit += 1
    if g.edge(g.vertex(random.randint(0, g.num_vertices()-1)), g.vertex(random.randint(0, g.num_vertices()-1))):
	randomhit += 1
  print "Attempts: "+ str(i)
  print "Predicted Hits: " + str(hit)
  print "Existing Edges: " + str(existing)
  print "Total edges: " + str(totaledges)
  print "Accuracy: " + str(float(hit)*100/float(totaledges)) + "%%"
  print "Random accuracy: " + str(float(randomhit)*100/float(totaledges)) + "%%"

def testWiSARD2(gprep, gtest):
    wisard = WiSARD()
    n = gprep.num_vertices()
    edge_possibilities = (n*(n-1))/2
    bit_string = makeBitString(gprep)
    #encoder = BitStringEncoder(int(math.sqrt(edge_possibilities)))
    encoder = BitStringEncoder(int(edge_possibilities/32))
    wisard.record(encoder(bit_string), "yes")

    test_string = makeBitString(gtest)

    random_graph = generateRandomGraph(gtest.num_vertices(), gtest.num_edges())
    empty_graph = generateRandomGraph(gtest.num_vertices(), 0)
    random_string = makeBitString(random_graph)
    empty_string = makeBitString(empty_graph)
    print "Test Graph has " + str(gtest.num_vertices()) + " vertices and " + str(gtest.num_edges()) + " edges."
    print "Random Graph has " + str(random_graph.num_vertices()) + " vertices and " + str(random_graph.num_edges()) + " edges."

    print "RAM Neurons:" + str(int(math.sqrt(edge_possibilities)))
    print "Possible edges:" + str(edge_possibilities)
    print "Answers:" + str(wisard.answers(encoder(test_string)))
    print "Random Answers:" + str(wisard.answers(encoder(random_string)))
    print "Empty Graph Answers:" + str(wisard.answers(encoder(empty_string)))


def generateRandomGraph(num_vertices, num_edges):
    g = Graph()
    for i in range(0, num_vertices):
	g.add_vertex()
    for i in range(0, num_edges):
	g.add_edge(g.vertex(random.randint(0, num_vertices-1)), g.vertex(random.randint(0, num_vertices-1)))
    print "Random graph generated!"
    return g

def thermometer(i, bits):
    if i > bits:
	i = bits
    return ("0"*(bits-i)) + ("1"*i)

def makeBitString(g, v, bits):
    bitstring = ""
    for u in g.vertices():
	edges = 0
	for e in g.edge(u, v, all_edges=True):
	    edges = edges+1
	bitstring += thermometer(edges, bits)
    return bitstring

def testWiSARD(u_bits, v_bits):
    wisard = WiSARD()
    encoder = BitStringEncoder(len(u_bits)/64)
    wisard.record(encoder(u_bits), "Edge")
    u_v = wisard.answers(encoder(v_bits))
    return u_v.values()[0]


def testPair(g, u, v, deg):
    u_bits = makeBitString(g, u, deg)
    v_bits = makeBitString(g, v, deg)

    u_v = testWiSARD(u_bits, v_bits)
    v_u = testWiSARD(v_bits, u_bits)
    #v_u = u_v
    return int(u_v+v_u)



def testPairs(g, gtest):
    rank = {}
    jaccardrank = {}
    num_vertices = g.num_vertices()
    max_deg = 0
    for i in range(0, num_vertices):
	if g.vertex(i).out_degree() > max_deg:
	    max_deg = g.vertex(i).out_degree()
    print "Maximum degree: " + str(max_deg)
    for u in range(0, num_vertices-1):
	for v in range(1, num_vertices):
	    if u == v:
		continue
	    #print makeBitString(g, g.vertex(u), 2) + "\n\n\n"
	    key = testPair(g, g.vertex(u), g.vertex(v), max_deg)
	    print "Testing pair " + str(u) + "," + str(v) + " = " + str(key)
	    key = key * 100000
	    while key in rank:
		key = key+1
	    jaccardscore = evaluatemodifiedjaccard(g, g.vertex(u), g.vertex(v), 1, 1)
	    rank[key] = (u,v)
	    jaccardrank[jaccardscore] = (u,v)
    items = sorted(rank.items())
    orderedrank = collections.OrderedDict(items, key=lambda t: t[0])
    testresults(rank, gtest)
    print "JACCARD"
    testresults(jaccardrank, gtest)



def testMetrics():
    gprep = load_graph("t2010-20125.xml.gz")
    rank = {}
    evaluategraph(gprep, 3, rank)
    items = sorted(rank.items())
    #items.reverse()
    orderedrank = collections.OrderedDict(items, key=lambda t: t[0])
    #print orderedrank

    gtest = load_graph("t20135.xml.gz")
    graphviz_draw(load_graph("t20135.xml.gz"))
    #gtest
    testresults(rank, gtest)
    #for e in gtest.edges():
    #print shortest_distance(gprep, gtest.vertex(e.source()), gtest.vertex(e.target()))

start = time.time()
gprep = load_graph("t2010-20125.xml.gz")
gtest = load_graph("t20135.xml.gz")
testPairs(gprep, gtest)
end = time.time()
print "Time elapsed: " + str(end-start)
#testMetrics()
