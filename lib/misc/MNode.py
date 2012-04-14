import csv, networkx as nx, matplotlib.pyplot as plt, pygraphviz as pgv, warnings, unidecode

# # Union Find, only useful in undirected graphs
# uf = nx.utils.UnionFind()
# for n1, n2 in diG.edges_iter():
#   uf.union(n1, n2)

def UnicodeDictReader(utf8_data, **kwargs):
  csv_reader = csv.DictReader(utf8_data, **kwargs)
  for row in csv_reader:
    yield dict([(key, unicode(value, 'utf-8')) for key, value in row.iteritems()])

def get_color(val, mode="green"):
  if mode == "green":
    return "#%02x%02x%02x%02x" % (50, 50, 50, min(255, float(val)/10 * 255)) 
  elif mode == "red":
    return "#%02x%02x%02x%02x" % (255, 0, 0, min(255, float(val)/5 * 255)) 

def csv_to_graph(filename, weighted_with_frequency=False):
  '''Convert a CSV file to an undirected graph'''
  g = nx.Graph()
  with open(filename, 'rb') as f:
    reader = UnicodeDictReader(f)
    for row in reader:
      if weighted_with_frequency is True:
        if g.has_edge(row['n1'], row['n2']):
          g[row['n1']][row['n2']]['weight'] += 1
        else:
          g.add_edge(row['n1'], row['n2'], weight=1)
      else:
        g.add_edge(row['n1'], row['n2'], weight=row['w'])
  return g
  
def csv_to_digraph(filename):
  '''Convert a CSV file to a directed graph'''
  g = nx.DiGraph()
  with open(filename, 'rb') as f:
    reader = UnicodeDictReader(f)
    for row in reader:
      if row['dir'] == '->':
        g.add_edge(row['n1'], row['n2'], weight=row['w'])
      elif row['dir'] == '<-':
        g.add_edge(row['n2'], row['n1'], weight=row['w'])
      else:
        g.add_edge(row['n1'], row['n2'], weight=row['w'])
        g.add_edge(row['n2'], row['n1'], weight=row['w'])
  return g
  
def graphviz_to_image(A, filename):
  '''Output a PyGraphViz graph object to an image'''
  print "Drawing..."
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    A.layout(prog='neato')
    A.draw(filename)
  # plt.clf()
  # pos = nx.graphviz_layout(G,prog="dot")
  # nx.draw(G, pos, node_size=20, alpha=0.5, edge_color='gray', with_labels=True, font_size=4)
  # plt.savefig('%s' % filename)

def format_graphviz(A):
  A.edge_attr['color'] = 'blue'
  A.node_attr['shape'] = 'point'
  A.edge_attr['arrowsize'] = '0.2'
  # A.node_attr['shape']='circle' # point
  # A.node_attr['width']='0.15'
  # A.node_attr['height']='0.15'
  # A.node_attr['fixedsize']='true'
  # A.node_attr['fontsize']='9'
  # A.node_attr['forcelabels']='true'
  # A.node_attr['style']='filled'
  # A.node_attr['color']='#bbbbbb'
  # A.node_attr['fillcolor']='#bbbbbb'
  # A.node_attr['fontname']='Helvetica'

def superposition(diG, G, remove_nodes=True):
  '''Superimpose the undirected graph G on the digraph diG,
    removing nodes in diG that are not in G if required,
    and highlighting edges in G in red where a path already exists
    in diG between those two nodes'''
  if remove_nodes is True:
    # Remove all nodes in diG that are not in G, but keep all connected paths
    keep_nodes = G.nodes()
    for n in diG.nodes():
      if n not in keep_nodes:
        for pre in diG.predecessors_iter(n):
          for suc in diG.successors_iter(n):
            diG.add_edge(pre, suc)
        diG.remove_node(n)
    remaining_num = len(diG.edges())
    print "Remaining edges after removal: %d" % remaining_num
    
  # Use MultiDiGraph so that conflicts can be shown with multiple paths from 1 node to another
  diG = nx.MultiDiGraph(diG) 
  A = nx.to_agraph(diG)
  format_graphviz(A)
  conflicts = 0 # keep a count of the number of "conflicts" (path exists)

  # Add G to diG without arrows since G is undirected,
  # and in red or green depending on whether a path exists between n1 and n2
  for n1, n2, data in G.edges_iter(data=True):
    if diG.has_node(n1) and diG.has_node(n2) and (nx.has_path(diG, n1, n2) or nx.has_path(diG, n2, n1)):
      A.add_edge(n1, n2, style="setlinewidth(1)", color=get_color(data['weight'], "red"), arrowsize=0.0)
      conflicts += float(data['weight'])
    else:
      A.add_edge(n1, n2, style="setlinewidth(1)", color=get_color(data['weight'], "green"), arrowsize=0.0)
  
  return (A, conflicts, remaining_num)

if __name__ == '__main__':
  import os
  dirs = [name for name in os.listdir('data/dependency_graphs') if os.path.isdir(os.path.join('data/dependency_graphs', name))]
  for diry in dirs:
    print diry
    directory = os.path.join('data/dependency_graphs', diry)
    with open('%s/200/conflicts_itemsets.txt' % directory, 'w') as f:
      writer = csv.writer(f)
      writer.writerow(["conflicts", "g_edges", "dig_edges", "dig_remaining"])
      i = 0
      while True:
        try:
          g, diG = csv_to_graph('%s/200/fq_%d.txt' % (directory, i)), csv_to_digraph('%s/200/dep_%d.txt' % (directory, i))
          a, conflicts, remaining_num = superposition(diG, g)
          graphviz_to_image(a, '%s/200/sup_fq_%d.svg' % (directory, i))
          print "Number of conflicts:", conflicts
          writer.writerow([conflicts, len(g.edges()), len(diG.edges()), remaining_num])
          i += 1
        except Exception as e:
          print e
          break

  # import os
  # dirs = [name for name in os.listdir('data/dependency_graphs') if os.path.isdir(os.path.join('data/dependency_graphs', name))]
  # for diry in dirs:
  #   print diry
  #   directory = os.path.join('data/dependency_graphs', diry)
  #   with open('%s/200/conflicts.txt' % directory, 'w') as f:
  #     writer = csv.writer(f)
  #     writer.writerow(["conflicts", "g_edges", "dig_edges", "dig_remaining"])
  #     i = 0
  #     while True:
  #       try:
  #         g, diG = csv_to_graph('%s/200/fc_%d.txt' % (directory, i)), csv_to_digraph('%s/200/dep_%d.txt' % (directory, i))
  #         a, conflicts, remaining_num = superposition(diG, g)
  #         graphviz_to_image(a, '%s/200/sup_%d.svg' % (directory, i))
  #         print "Number of conflicts:", conflicts
  #         writer.writerow([conflicts, len(g.edges()), len(diG.edges()), remaining_num])
  #         i += 1
  #       except Exception as e:
  #         print e
  #         break