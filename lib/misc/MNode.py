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

# Convert a CSV file into an undirected graph
# Weighted with frequency - increase weight by 1 every time an edge is seen
# Replace higher - Replace weight only if a higher weight is seen
def csv_to_graph(filename, weighted_with_frequency=False, replace_higher=True):
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
        if replace_higher is True:
          if g.has_edge(row['n1'], row['n2']):
            if g.edge[row['n1']][row['n2']]['weight'] < row['w']:
              g.edge[row['n1']][row['n2']]['weight'] = row['w']
          else:
            g.add_edge(row['n1'], row['n2'], weight=row['w'])
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
  
def graphviz_to_image(A, filename, prog='neato'):
  '''Output a PyGraphViz graph object to an image'''
  print "Drawing..."
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    A.layout(prog=prog)
    A.draw(filename)
  # plt.clf()
  # pos = nx.graphviz_layout(G,prog="dot")
  # nx.draw(G, pos, node_size=20, alpha=0.5, edge_color='gray', with_labels=True, font_size=4)
  # plt.savefig('%s' % filename)

def format_graphviz(A):
  A.edge_attr['color'] = 'blue'
  A.node_attr['shape'] = 'point'
  A.edge_attr['arrowsize'] = '0.2'
  
def format_graphviz_labels(A):
  # A.node_attr['shape']='circle' # point
  # A.node_attr['width']='0.15'
  # A.node_attr['height']='0.15'
  # A.node_attr['fixedsize']='true'
  A.edge_attr['color'] = 'blue'
  A.node_attr['fontsize']='9'
  A.node_attr['forcelabels']='true'
  A.node_attr['style']='filled'
  A.node_attr['color']='#bbbbbb'
  A.node_attr['fillcolor']='#bbbbbb'
  A.node_attr['fontname']='Helvetica'
  
def filter_graph(g, threshold=0.01):
  g2 = nx.Graph()
  edgys = [(n1, n2, data, float(data['weight'])) for n1, n2, data in g.edges_iter(data=True)]
  edgys = sorted(edgys, key=lambda x: -x[3])
  for n1, n2, data, _ in edgys[0:int(len(edgys)*threshold)]:
    g2.add_edge(n1, n2, attr_dict=data)
  return g2

def graph_to_graphviz(G, labels=False):
  A = nx.to_agraph(nx.Graph())
  if labels:
    format_graphviz_labels(A)
  else:
    format_graphviz(A)
  for n1, n2, data in G.edges_iter(data=True):
    A.add_edge(n1, n2, style="setlinewidth(1)", color=get_color(data['weight'], "green"), arrowsize=0.0)
  return A

def superposition(diG, G, remove_nodes=True, labels=False):
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
  print "Remaining edges (after removal): %d" % remaining_num

  # Use MultiDiGraph so that conflicts can be shown with multiple paths from 1 node to another
  diG = nx.MultiDiGraph(diG) 
  A = nx.to_agraph(diG)
  if labels:
    format_graphviz_labels(A)
  else:
    format_graphviz(A)
  conflicts = [] # keep a list of the number of "conflicts" (path exists)

  # Add G to diG without arrows since G is undirected,
  # and in red or green depending on whether a path exists between n1 and n2
  for n1, n2, data in G.edges_iter(data=True):
    if diG.has_node(n1) and diG.has_node(n2) and (nx.has_path(diG, n1, n2) or nx.has_path(diG, n2, n1)):
      A.add_edge(n1, n2, style="setlinewidth(1)", color=get_color(data['weight'], "red"), arrowsize=0.0)
      conflicts.append((str(n1), str(n2), float(data['weight'])))
    else:
      A.add_edge(n1, n2, style="setlinewidth(1)", color=get_color(data['weight'], "green"), arrowsize=0.0)
  
  return (A, conflicts, remaining_num)

def superposition_dir(diG, G, remove_nodes=True, labels=False, conflict_distance=5):
  '''Superimpose the undirected graph G on the digraph diG,
    removing nodes in diG that are not in G if required,
    and highlighting edges in G in red where a path already exists
    in diG between those two nodes'''
    
  # Return the least common ancestor of 2 nodes in a tree, and the distance between them
  def lca_dist(diG, n1, n2):
    if n1 == n2:
      return (n1, 0)
    # Build a hash from n1 to the root
    n1_hash, n1_curr, n1_dist = { n1 : 0 }, n1, 0
    while diG.in_degree(n1_curr) > 0:
      n1_curr = diG.predecessors(n1_curr)[0]
      n1_dist += 1
      n1_hash[n1_curr] = n1_dist
    # Go from n2 to root, and see if we encounter n1 at any point
    n2_curr, n2_dist = n2, 0
    if n2_curr in n1_hash:
      return (n2_curr, n1_hash[n2_curr])
    while diG.in_degree(n2_curr) > 0:
      n2_curr = diG.predecessors(n2_curr)[0]
      n2_dist += 1
      if n2_curr in n1_hash:
        return (n2_curr, n2_dist + n1_hash[n2_curr])
    # Nothing found
    return (None, float("inf"))
    
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
  print "Remaining edges (after removal): %d" % remaining_num

  # Use MultiDiGraph so that conflicts can be shown with multiple paths from 1 node to another
  diG = nx.MultiDiGraph(diG) 
  A = nx.to_agraph(diG)
  if labels:
    format_graphviz_labels(A)
  else:
    format_graphviz(A)
  conflicts = [] # keep a list of the number of "conflicts" (path exists)

  # Add G to diG without arrows since G is undirected,
  # and in red or green depending on whether a path exists between n1 and n2
  for n1, n2, data in G.edges_iter(data=True):
    if diG.has_node(n1) and diG.has_node(n2):
      lca_node, lca_distance = lca_dist(diG, n1, n2) # Compute LCA distance
      if lca_distance >= conflict_distance:
        A.add_edge(n1, n2, style="setlinewidth(1)", color=get_color(data['weight'], "red"), arrowsize=0.0)
        conflicts.append((str(n1), str(n2), float(data['weight']), lca_distance))
    else:
      A.add_edge(n1, n2, style="setlinewidth(1)", color=get_color(data['weight'], "green"), arrowsize=0.0)
  
  return (A, conflicts, remaining_num)

if __name__ == '__main__':
  pass