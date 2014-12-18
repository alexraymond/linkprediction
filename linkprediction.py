from graph_tool.all import *
import random
g2 = load_graph("connected.xml.gz")
g = g2.copy()

print g.num_vertices()
print g.num_edges()
print g.is_directed()

def filteredges(g, fromyear, toyear):
  edgefilter = g.new_edge_property("bool")
  edgeages = g.edge_properties["age"]
  for e in g.edges():
    if edgeages[e] >= fromyear and edgeages[e] <= toyear:
      edgefilter[e] = True
    else:
      edgefilter[e] = False
  return edgefilter

def filteredgescolor(g, fromyear, toyear):
  edgefilter = g.new_edge_property("string")
  edgeages = g.edge_properties["age"]
  for e in g.edges():
    if edgeages[e] >= fromyear and edgeages[e] <= toyear:
      edgefilter[e] = "red"
    else:
      edgefilter[e] = "blue"
  return edgefilter

def filtervertices(g, degree):
  print "Filter it"
  vertexfilter = g.new_vertex_property("bool")
  for v in g.vertices():
    if v.out_degree() >= degree:
      vertexfilter[v] = True
    else:
      vertexfilter[v] = False
  return vertexfilter

def minimumdegree(g, degree):
  i = True
  while i is True:
    print "Let's do it"
    edges = g.num_edges()
    g.set_vertex_filter(filtervertices(g, degree))
    g.purge_vertices()
    if edges == g.num_edges():
      break
    print g.num_vertices()
    print g.num_edges()
    i = False
    for v in g.vertices():
      if v.out_degree() >= degree:
	i = True
	break
def assignindexes(g):
  vertexindexes = g.new_vertex_property("int")
  i = 0
  for v in g.vertices():
    vertexindexes[v] = i
    i += 1
  g.vertex_properties["index"] = vertexindexes
  
def shrinknetwork(g, p):
  toremove = g.new_vertex_property("bool")
  for v in g.vertices():
    if p > random.uniform(0, 1):
      toremove[v] = True
    else:
      toremove[v] = False
  return toremove

def shrinknetworkbydistance(g, alpha):
  toremove = g.new_vertex_property("bool")
  highestdegreevertex = g.vertex(0)
  for v in g.vertices():
    if v.out_degree() > highestdegreevertex.out_degree():
      highestdegreevertex = v
  for v in g.vertices():
    shortestdistance = shortest_distance(g, highestdegreevertex, v)
    if shortestdistance == 0:
      p = 1.0 
    elif shortestdistance > 6:
      p = 0.0
    else:
      p = (0.3) / shortest_distance(g, highestdegreevertex, v)**3
    if p > random.uniform(0, 1):
      toremove[v] = True
    else:
      toremove[v] = False
  return toremove
    

yearfilter = filteredges(g, 2010, 2013)
g.set_edge_filter(yearfilter)
g.purge_edges()
print "2010-2013 vertices:" + str(g.num_vertices())
print "2010-2013 edges:" + str(g.num_edges())
toremove = shrinknetwork(g, 0.70)
g.set_vertex_filter(toremove)
g.purge_vertices()
degree = 5
minimumdegree(g, degree)
#g.vertex_properties["index"] = g.vertex_index
assignindexes(g)

print "2010-2013 vertices:" + str(g.num_vertices())
print "2010-2013 edges:" + str(g.num_edges())
smallg = g.copy()

bicomp, articulation, nc = label_biconnected_components(smallg)
smallg.set_vertex_filter(articulation, True)
smallg.purge_vertices()
print "2010-2013 vertices:" + str(smallg.num_vertices())
print "2010-2013 edges:" + str(smallg.num_edges())
smallg.set_vertex_filter(label_largest_component(smallg))
smallg.purge_vertices()
print "2010-2013 vertices:" + str(smallg.num_vertices())
print "2010-2013 edges:" + str(smallg.num_edges())
assignindexes(smallg)

g2010_2012 = smallg.copy()
g2013 = smallg.copy()

yearfilter = filteredges(g2010_2012, 2010, 2012)
g2010_2012.set_edge_filter(yearfilter)
g2010_2012.purge_edges()

yearfilter = filteredges(g2013, 2013, 2013)
g2013.set_edge_filter(yearfilter)
g2013.purge_edges()

print "2010-2012"
print g2010_2012.num_vertices()
print g2010_2012.num_edges()
print "2013"
print g2013.num_vertices()
print g2013.num_edges()
g.save("2010-2013.xml.gz")

g2010_2012.save("t2010-20125.xml.gz")
g2013.save("t20135.xml.gz")
smallg.save("tinyg5.xml.gz")
graphviz_draw(smallg, ecolor=filteredgescolor(smallg, 2013, 2013))