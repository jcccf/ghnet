import csv, networkx as nx, matplotlib.pyplot as plt, pygraphviz as pgv

def csv_to_graph(filename):
  g = nx.Graph()
  with open(filename, 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
      g.add_edge(row['n1'], row['n2'])
  return g
  
def csv_to_digraph(filename):
  g = nx.DiGraph()
  with open(filename, 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
      if row['dir'] == '->':
        g.add_edge(row['n1'], row['n2'])
      else:
        g.add_edge(row['n2'], row['n1'])
  return g
  
def graphviz_to_image(A, filename):
  A.layout(prog='dot')
  A.draw(filename)
  # plt.clf()
  # pos = nx.graphviz_layout(G,prog="dot")
  # nx.draw(G, pos, node_size=20, alpha=0.5, edge_color='gray', with_labels=True, font_size=4)
  # plt.savefig('%s' % filename)
  
def superposition(G1, G2):
  keep_nodes = G2.nodes()
  for n in G1.nodes():
    if n not in keep_nodes:
      for pre in G1.predecessors_iter(n):
        for suc in G1.successors_iter(n):
          G1.add_edge(pre, suc)
      G1.remove_node(n)
  print G1.edges()
  
  G1 = nx.MultiDiGraph(G1)
    
  A = nx.to_agraph(G1)
  A.edge_attr['color'] = 'red'
  # A.node_attr['shape']='point'
  A.node_attr['shape']='circle'
  A.node_attr['width']='0.15'
  A.node_attr['height']='0.15'
  A.node_attr['fixedsize']='true'
  A.node_attr['fontsize']='9'
  A.node_attr['forcelabels']='true'
  A.node_attr['style']='filled'
  A.node_attr['color']='#bbbbbb'
  A.node_attr['fillcolor']='#bbbbbb'
  A.node_attr['fontname']='Helvetica'
  for n1, n2 in G2.edges_iter():
    A.add_edge(n1, n2, style='setlinewidth(1)', color='green', arrowsize=0.0)
  # for node in A.nodes():
  #   A.add_node(str(node)+"_text", label=str(node), shape='plaintext')
  #   A.add_edge(node, str(node)+"_text", style='invis')
  return A

if __name__ == '__main__':
  g = csv_to_graph('list.txt')
  g2 = csv_to_digraph('rails_dep.txt')
  a = superposition(g2, g)
  graphviz_to_image(a, 'list.svg') 