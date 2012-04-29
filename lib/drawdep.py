from misc import *
from plot import *
import os, csv, glob, json

n = "200"

dirs = [name for name in os.listdir('data/dependency_graphs') if os.path.isdir(os.path.join('data/dependency_graphs', name))]

def make_directories(directory):
  for d in ['auth_fq']:
    out_dir = os.path.join(directory, d)
    if not os.path.exists(out_dir):
      os.makedirs(out_dir)

class Aggregator:
  def __init__(self):
    self.cs_all = {}
  
  def add(self, new_hash):
    cs = [v for k, v in sorted(new_hash.items(), key = lambda x:x[0])]
    for i, c in enumerate(cs):
      self.cs_all.setdefault(i, []).append(c)

  def avg(self):
    return {k: sum(v)/len(v) for k, v in self.cs_all.iteritems()}

# Generate basic conflict count  
def conflict_graph(directory, conflict_filename):
  cdict, cdict_frac, i = {}, {}, 1
  with open(directory+"/%s.txt" % conflict_filename, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      print row['conflicts'], row['dig_remaining']
      cdict[i] = float(row['conflicts'])
      cdict_frac[i] = float(row['conflicts'])/float(row['dig_remaining']) if float(row['dig_remaining']) > 0 else 0
      i += 1
  if len(cdict) > 0:
    BasicPlot.plot_twoscales("%s/%s" % (directory, conflict_filename), [cdict, cdict_frac], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps']) 
  else:
    print "No data"
  return (cdict, cdict_frac)

class ConflictGraphAggregator:
  def __init__(self, conflict_name='fq', base_name='dir'):
    self.conflict_name = conflict_name
    self.base_name = base_name
    self.cs_all = Aggregator()
    self.cs_fracs_all = Aggregator()
    
  def generate_and_add(self, directory):
    # Generate # of Conflicts
    cs, cs_fracs = conflict_graph(os.path.join(directory, "%s_%s" % (self.conflict_name, self.base_name)), "all_conflicts_%s_%s" % (self.conflict_name, self.base_name))
    self.cs_all.add(cs) # Generate stuff for average
    self.cs_fracs_all.add(cs_fracs)
    
  def plot_agg(self):
    BasicPlot.plot_twoscales("data/dependency_graphs/all_conflicts_%s_%s" % (self.conflict_name, self.base_name), [self.cs_all.avg(), self.cs_fracs_all.avg()], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps'])

fqdir = ConflictGraphAggregator('fq', 'dir')
fqdep = ConflictGraphAggregator('fq', 'dep')
fcdep = ConflictGraphAggregator('fc', 'dep')
for diry in dirs:
  directory = os.path.join('data/dependency_graphs', diry, str(n))
  print directory
  make_directories(directory)
  
  # # Generate Graphs for Itemset Occurrences
  # for filename in glob.iglob(directory+'/itemset_occurrences/*.txt'):
  #   with open(filename, 'r') as f:
  #     iset = json.loads(f.read())
  #     print iset['itemset']
  #     xy_list = [(i,float(x)) for i, x in enumerate(iset['occurrences'])]
  #     other_xy_lists = [[(i, float(x)) for i, x in enumerate(xs)] for xs in iset['items'].itervalues()]
  #     DistributionPlot.scatter_plot(filename.rsplit(".", 1)[0], xy_list, other_xy_lists=other_xy_lists, sliding_window=10, title=str(iset['itemset']))

  # Generate conflict graphs over time
  fqdir.generate_and_add(directory)
  fqdep.generate_and_add(directory)
  fcdep.generate_and_add(directory)
  
  # Generate Unique Authors and # of Frequent Itemsets
  authors, frequent_edges = {}, {}
  for filename in glob.iglob(directory+"/af_*.txt"):
    i = int(filename.rsplit("af_", 1)[1].split(".")[0])
    with open(filename, 'r') as f:
      af = json.loads(f.read())
      authors[i] = len(af)
    g = MNode.csv_to_graph(directory+"/fq_%d.txt" % i)
    frequent_edges[i] = len(g.edges())
  print authors, frequent_edges
  BasicPlot.plot_twoscales(directory+"/auth_fq/auth_fq_%s_%s" % (diry str(n)), [authors, frequent_edges], labels=["Authors", "# of Frequent Itemset Edges"])
  
fqdir.plot_agg()
fqdep.plot_agg()
fcdep.plot_agg()

# # Convert SVGs to PNGs
# import subprocess
# for diry in dirs:
#   directory = os.path.join('data/dependency_graphs', diry, str(n))
#   print directory
#   p = subprocess.Popen("mogrify -density 144 -format png %s/*.svg" % directory,shell=True)
#   out,err = p.communicate()