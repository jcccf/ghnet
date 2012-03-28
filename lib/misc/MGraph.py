import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

def draw_fork_trees(db):
  # Get all unique trees
  shell_levels = {}
  roots = db.q('SELECT DISTINCT root_gname FROM forks')
  for r in roots:
    root = r[0]
    root_node = db.q('SELECT * FROM forks WHERE root_gname = "%s" AND gno = 0 AND parent_glogin IS NULL LIMIT 1' % root)
    root_node = "%s/%s" % (root_node[0][0], root_node[0][1])
    G = nx.DiGraph()
    nodes = db.q('SELECT * FROM forks WHERE root_gname = "%s" AND gno = 0 AND parent_glogin IS NOT NULL' % root)
    for node in nodes:
      parent_node = "%s/%s" % (node[3], node[4])
      child_node = "%s/%s" % (node[0], node[1])
      G.add_edge(parent_node, child_node)
    pos = nx.graphviz_layout(G,prog="twopi",root=root_node)
    nx.draw(G, pos, node_size=20, alpha=0.5, edge_color='gray', with_labels=False)
    xmax=1.02*max(xx for xx,yy in pos.values())
    ymax=1.02*max(yy for xx,yy in pos.values())
    plt.xlim(0,xmax)
    plt.ylim(0,ymax)
    plt.savefig('data/graphs/forks/%s.svg' % root)
    plt.savefig('data/graphs/forks/%s.png' % root)
    plt.clf()

def groups(lin):
  groups = []
  prev, prev_idx = None, 0
  for i, val in enumerate(lin):
    if val == prev:
      pass
    else:
      if prev is not None:
        groups.append((prev, prev_idx))
      prev = val
      prev_idx = i
  if prev is not None:
    groups.append((prev, prev_idx))
  return groups

def draw_lineage(lineage, root='hello'):
  plt.clf()
  G = nx.DiGraph()
  
  # print lineage
  
  # Remove empty lists from head
  # while len(lineage) > 0 and len(lineage[0]) == 0:
  #   lineage.pop(0)
  
  for i, lin in enumerate(lineage):
    prev = None
    groupies = groups(lin)
    
    # Only link if not starting at the root
    if i > 0:
      # If the current level is blank, link a virtual node to all previous groups
      # (i, 0, 0) -> all groups in prev level (this happens when the whole file got deleted in a commit)
      if len(lin) == 0:
        for group, idx in groups(lineage[i-1]):
          if isinstance(group, tuple):
            G.add_edge((i-1,)+group, (i,)+(0,0))    
      # If there's only 1 group, and it is of the form (-1,-2) or (-1,-1) or (<0, <0)
      # meaning there's nothing before it, so link it to the virtual previous node (i-1, 0, 0)
      if len(groupies) == 1 and isinstance(groupies[0][0], tuple) and groupies[0][0][0] < 0 and groupies[0][0][1] < 0:
        G.add_edge((i-1,)+(0,0), (i,)+groupies[0][0])
        continue
    
    # If not, proceed as normal
    for group, idx in groupies:
      if isinstance(group, tuple) and i > 0:
        # Find overlap with any earlier groups
        parents = set()
        prev_lin = lineage[i-1]
        # print i, group
        for j in range(group[0], group[1]+1):
          if isinstance(prev_lin[j], tuple):
            parents.add((i-1,)+prev_lin[j])
          else:
            base, n = prev_lin[j], -1
            while not isinstance(base, tuple):
              n -= 1
              base = lineage[i+n][base]
            parents.add((i+n,)+base)
        for p in parents:
          G.add_edge(p, (i,)+group)
            
  # Generate Graph
  pos = nx.graphviz_layout(G,prog="dot")
  nx.draw(G, pos, node_size=20, alpha=0.5, edge_color='gray', with_labels=False)
  if len(pos.values()) > 0: # Is this right?
    xmax=1.02*max(xx for xx,yy in pos.values())
    ymax=1.02*max(yy for xx,yy in pos.values())
    plt.xlim(0,xmax)
    plt.ylim(0,ymax)
    info = dag_info(G)
    plt.text(.1, .1, 'dia %d / ht %d' % (info['diameter'], info['height']))
  else:
    info = {'diameter': 0, 'height': 0, 'nodes': 0, 'edges': 0}
  root = root.replace('/', '|')
  plt.savefig('data/graphs/file_hist/%s.svg' % root)
  plt.savefig('data/graphs/file_hist/%s.png' % root)
  # print G.edges()
  return (G, info)

# G = nx.DiGraph()
# G.add_edge("hi","world")
# nx.draw(G)
# plt.show()

def dag_info(graph):
  g = graph.to_undirected()
  diameter = nx.diameter(g)
  root = [n for n, d in graph.in_degree().items() if d == 0][0]
  height = nx.eccentricity(g, root) # TODO FIX
  return {'diameter': diameter, 'height': height, 'nodes': len(graph), 'edges': len(graph.edges())}

def paths_to_leaves(digraph, sort_paths=False):
  '''Return paths from the root of the graph to each leaf. A path is a list of commits'''
  if len(digraph.nodes()) > 0:
    root = [n for n in digraph.nodes() if digraph.in_degree(n) == 0][0]
    leaves = [n for n in digraph.nodes() if digraph.out_degree(n) == 0]
    neg_graph = nx.DiGraph(digraph)
    for u, v in neg_graph.edges():
      neg_graph[u][v]['weight'] = -1
    pred, dist = nx.bellman_ford(neg_graph, root)
    dist_paths = []
    for leaf in leaves:
      path = [leaf]
      curr = leaf
      while pred[curr] is not None:
        curr = pred[curr]
        path.append(curr)
      path.reverse()
      dist_paths.append((-dist[leaf], path))
    if sort_paths is True:
      dist_paths = sorted(dist_paths, key=lambda x:-x[0])
    return dist_paths
  else:
    return None

if __name__ == '__main__':
  lin = [[(-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2)], [0, 1, 2, 3, (3, 4), 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, (3, 10), (3, 10), (3, 10), (3, 10), (3, 10), (3, 10), (3, 10), (3, 10), (3, 10)], [0, (0, 2), 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 1, 2, 3, (3, 4), 4, 5, 6, 7, 8, 9, 10, 11, 12], [(0, 0), (0, 0), (0, 0), 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, (14, 15), (14, 15), (14, 15), 15, 16], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, (18, 19)], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, (18, 19), (18, 19)], [0, 1, 2, (2, 6), (2, 6), (2, 6), 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, (19, 20), (19, 20), (19, 20), (19, 20)], [0, 1, 2, 3, 4, 5, 6, 7, 8, (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), 14, 15, 16, 17, 18, 19, 20, 21, 22], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 26, 27, 28, 29, 30, 31, 32, (32, 33), (32, 33), (32, 33), 33, 34], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, (10, 12), 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]]
  G, info = draw_lineage(lin)
  print paths_to_leaves(G, sort_paths=True)
  # print group(lin[1])