import xml.etree.cElementTree as ET
from collections import defaultdict
from graph_tool.all import *
filepath = "dblp3.xml"
context = ET.iterparse(filepath, events = ("start", "end"))

context = iter(context)
onArticleTag = False
currentArticle = ''
currentYear = 0
counter = 0
d = defaultdict(list)
authorlist = list()
articleyears = {}
for event, elem in context:
  tag = elem.tag
  value = elem.text  
  if value:
    value = value.encode('utf-8').strip()
    
  if event == 'start':
    if tag == "article":
      #print authorlist
      if len(authorlist) > 1:
	for k,v in authorlist:
	  if articleyears[counter] is None:
	    counter -= 1
	    break
	  d.setdefault(k, []).append(v)
	authorlist = []
	counter += 1
	if not counter % 8524:
	  print str(counter/8524) + "%"
      #print "ARTICLE: %s" % currentArticle
    elif tag == "author":
      #print counter, value
      authorlist.append((counter, value))
      #print "(" + str(currentYear) + ")" + "On article " + str(currentArticle) + ": " + str(value)
    elif tag == "title":
      currentArticle = value
    elif tag == "year":
      currentYear = value
      articleyears[counter] = value
  elem.clear()

print "Isolating repeated authors..."
#isolates repeated authors
authorset = set()
for k in d:
  for author in d[k]:
    authorset.add(author)

print "Creating int values for authors..."
#creates int values for authors
authorindexes = {}
counter = 0
for author in authorset:
  authorindexes[author] = counter
  counter += 1
  
#creates graph
g = Graph()
g.set_directed(False)
g.set_fast_edge_removal()
  
print "Creating vertices..."
#adds vertices
for author in authorset:
  g.add_vertex()
print "Vertices created!"

edgeages = g.new_edge_property("int")

print "Creating edges..."
#adds edges
for articleindex in d:
  year = articleyears[articleindex]
  i = 0
  j = 1
  while j < len(d[articleindex]):
    while i < j:
      if articleyears[articleindex] is None:
	break
      u = authorindexes[d[articleindex][i]]
      v = authorindexes[d[articleindex][j]]
      g.add_edge(g.vertex(u), g.vertex(v))
      
      edgeages[g.edge(u,v)] = int(articleyears[articleindex])
      #print str(articleyears[articleindex])
      i += 1
    j += 1

print "Edges created!"
g.edge_properties["age"] = edgeages

print "Vertices: " + str(g.num_vertices())
print "Edges: " + str(g.num_edges())

comp, hist = label_components(g)

components = set()
for i in comp.a:
  components.add(i)
  
print "Number of components: " + str(len(components))

l = label_largest_component(g)
largestcomponent = l.copy()
i = 0
g2 = GraphView(g, vfilt=largestcomponent)
remove_self_loops(g2)
g2.purge_vertices()
print "Largest component size: " + str(g2.num_vertices())

print "Vertices: " + str(g2.num_vertices())
print "Edges: " + str(g2.num_edges())

#.save("graph.xml.gz")
g2.save("small.xml.gz")
diameter, ends = pseudo_diameter(g2)
print "Diameter: " + str(diameter)

#graph_draw(g2)
#print d.items()
#print articleyears
#print len(articleyears)