from misc import *
import csv, os, os.path, glob

def make_directories(directory):
  for d in ['author', 'itemset']:
    out_dir = os.path.join(directory, d)
    if not os.path.exists(out_dir):
      os.makedirs(out_dir)

def author_collaboration_graph(directory, i):
  g = MNode.csv_to_graph('%s/au_%d.txt' % (directory, i))
  a = MNode.graph_to_graphviz(g)
  MNode.graphviz_to_image(a, '%s/author/g_au_%d.svg' % (directory, i))

def itemset_graph(directory, i):
  g = MNode.csv_to_graph('%s/fq_%d.txt' % (directory, i))
  a = MNode.graph_to_graphviz(g)
  MNode.graphviz_to_image(a, '%s/itemset/g_it_%d.svg' % (directory, i))
  # Most Frequent with Labels
  g = MNode.filter_graph(g)
  a = MNode.graph_to_graphviz(g, labels=True)
  MNode.graphviz_to_image(a, '%s/itemset/g_it_%d_dot.svg' % (directory, i), prog="dot")

# Superimpose a conflict graph with a base graph structure, commonly either a
# file directory graph or a file dependency graph
class CommitConflicts:
  def __init__(self, directory, conflict_name='fq', base_name='dir', superposition_fn = MNode.superposition):
    self.directory = directory
    self.out_directory = os.path.join(directory, "%s_%s" % (conflict_name, base_name))
    if not os.path.exists(self.out_directory):
      os.makedirs(self.out_directory)
    self.conflict_name = conflict_name
    self.base_name = base_name
    self.f = open('%s/all_conflicts_%s_%s.txt' % (self.out_directory, self.conflict_name, self.base_name), 'w')
    self.writer = csv.writer(self.f)
    self.writer.writerow(["conflicts", "g_edges", "dig_edges", "dig_remaining"])
    self.superposition_fn = superposition_fn
    
  def conflicts(self, i):
    # Itemset Conflicts on Dir
    g, diG = MNode.csv_to_graph('%s/%s_%d.txt' % (self.directory, self.conflict_name, i)), MNode.csv_to_digraph('%s/%s_%d.txt' % (self.directory, self.base_name, i))
    a, conflicts, remaining_num = self.superposition_fn(diG, g, False)
    MNode.graphviz_to_image(a, '%s/g_%s_%s_%d.svg' % (self.out_directory, self.conflict_name, self.base_name, i))
    # a, conflicts, remaining_num = self.superposition_fn(diG, g, False, True)
    # MNode.graphviz_to_image(a, '%s/g_%s_%s_%d_dot.svg' % (self.out_directory, self.conflict_name, self.base_name, i), prog='dot')
    # Write out conflicted edges to CSV in descending # of conflicts
    with open('%s/conflicts_%s_%s_%d.txt' % (self.out_directory, self.conflict_name, self.base_name, i), 'w') as f:
      iswriter = csv.writer(f)
      iswriter.writerow(["n1", "n2", "conflicts"])
      for x in sorted(conflicts, key=lambda x: -x[2]):
        iswriter.writerow(x)
    num_conflicts = sum([x[2] for x in conflicts])
    print "Conflicts for %s %s: %d" % (self.conflict_name, self.base_name, num_conflicts)
    self.writer.writerow([num_conflicts, len(g.edges()), len(diG.edges()), remaining_num])
    
  def close(self):
    self.f.close()

if __name__ == '__main__':  
  n = 200
  dirs = [name for name in os.listdir('data/dependency_graphs') if os.path.isdir(os.path.join('data/dependency_graphs', name))]
  for diry in dirs:
    print diry
    directory = os.path.join('data/dependency_graphs', diry, str(n))
    make_directories(directory)
    conflicts_fq_dir = CommitConflicts(directory, 'fq', 'dir', superposition_fn=MNode.superposition_dir)
    conflicts_fq_dep = CommitConflicts(directory, 'fq', 'dep')
    conflicts_fc_dep = CommitConflicts(directory, 'fc', 'dep')
    for filename in glob.iglob(directory+"/fq_*.txt"):
      i = int(filename.rsplit("fq_", 1)[1].split(".")[0])
      # Itemset Conflicts on Directory Graph
      conflicts_fq_dir.conflicts(i)
      conflicts_fq_dep.conflicts(i)
      conflicts_fc_dep.conflicts(i)
      # Generate Author Collaboration Graph
      author_collaboration_graph(directory, i)
      # Generate Itemset Graph (and 1 with labels)
      itemset_graph(directory, i)
    conflicts_fq_dir.close()
    conflicts_fq_dep.close()
    conflicts_fc_dep.close()