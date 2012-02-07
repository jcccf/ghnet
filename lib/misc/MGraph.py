import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

def draw_fork_trees(db):
  # Get all unique trees
  shell_levels = {}
  roots = db.q('SELECT DISTINCT root_gname FROM forks')
  for r in roots:
    root = r[0]
    root_node = db.forks.where('root_gname = "%s" AND gno = 0 AND parent_glogin IS NULL LIMIT 1' % root)
    root_node = "%s/%s" % (root_node[0][0], root_node[0][1])
    G = nx.DiGraph()
    nodes = db.forks.where('root_gname = "%s" AND gno = 0 AND parent_glogin IS NOT NULL' % root)
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
    plt.savefig('%s.svg' % root)
    plt.savefig('%s.png' % root)
    plt.clf()

# G = nx.DiGraph()
# G.add_edge("hi","world")
# nx.draw(G)
# plt.show()