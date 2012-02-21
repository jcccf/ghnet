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
  G = nx.DiGraph()
  for i, lin in enumerate(lineage):
    prev = None
    for group, idx in groups(lin):
      if isinstance(group, tuple) and i > 0:
        # Find overlap with any earlier groups
        parents = set()
        prev_lin = lineage[i-1]
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
  pos = nx.graphviz_layout(G,prog="dot")
  nx.draw(G, pos, node_size=20, alpha=0.5, edge_color='gray', with_labels=False)
  xmax=1.02*max(xx for xx,yy in pos.values())
  ymax=1.02*max(yy for xx,yy in pos.values())
  plt.xlim(0,xmax)
  plt.ylim(0,ymax)
  plt.savefig('data/graphs/file_hist/%s.svg' % root)
  plt.savefig('data/graphs/file_hist/%s.png' % root)
  print G.edges()

# G = nx.DiGraph()
# G.add_edge("hi","world")
# nx.draw(G)
# plt.show()

if __name__ == '__main__':
  #lin = [[(-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2)], [0, (1, 6), (1, 6), (1, 6), (1, 6), (1, 6), (1, 6), (1, 6), 7, 8, 9], [0, (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10)], [(0, 4), (0, 4), (0, 4), (0, 4), (0, 4), 5, 6, 7, 8, 9, 10, 11, 12], [0, (1, 6), (1, 6), (1, 6), (1, 6), (1, 6), (1, 6), (1, 6), 7, 8, 9, 10, 11, 12], [(0, 2), (0, 2), (0, 2), (0, 2), (0, 2), (0, 2), 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, (12, 16), (12, 16), (12, 16), (12, 16), (12, 16), (12, 16), (12, 16), (12, 16)], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, (16, 19), (16, 19), (16, 19), (16, 19)], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, (16, 19), (16, 19), (16, 19), (16, 19), (16, 19)], [(0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], [0, (1, 7), (1, 7), (1, 7), (1, 7), (1, 7), (1, 7), 8, 9, 10, 11, 12, 13, 14, 15, 16, (17, 20), (17, 20), (17, 20), (17, 20), (17, 20), (17, 20), (17, 20)], [0, 1, 2, 3, 4, 5, (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), (6, 16), 17, 18, 19, 20, 21, 22], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, (20, 28), (20, 28), (20, 28), (20, 28), (20, 28), (20, 28), 29, (30, 34), (30, 34), (30, 34), (30, 34), (30, 34), (30, 34), (30, 34), (30, 34)], [0, 1, 2, 3, 4, 5, 6, 7, (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]]
  lin = [[(-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2), (-1, -2)], [0, 1, 2, 3, (3, 4), 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, (3, 10), (3, 10), (3, 10), (3, 10), (3, 10), (3, 10), (3, 10), (3, 10), (3, 10)], [0, (0, 2), 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [0, 1, 2, 3, (3, 4), 4, 5, 6, 7, 8, 9, 10, 11, 12], [(0, 0), (0, 0), (0, 0), 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, (14, 15), (14, 15), (14, 15), 15, 16], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, (18, 19)], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, (18, 19), (18, 19)], [0, 1, 2, (2, 6), (2, 6), (2, 6), 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, (19, 20), (19, 20), (19, 20), (19, 20)], [0, 1, 2, 3, 4, 5, 6, 7, 8, (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), (8, 14), 14, 15, 16, 17, 18, 19, 20, 21, 22], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 26, 27, 28, 29, 30, 31, 32, (32, 33), (32, 33), (32, 33), 33, 34], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, (10, 12), 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]]
  draw_lineage(lin)
  # print group(lin[1])