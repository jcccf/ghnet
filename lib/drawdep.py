from misc import *
from plot import *
import os, csv, glob, json

n = 200

dirs = [name for name in os.listdir('data/dependency_graphs') if os.path.isdir(os.path.join('data/dependency_graphs', name))]

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
  BasicPlot.plot_twoscales("%s/%s" % (directory, conflict_filename), [cdict, cdict_frac], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps']) 
  return (cdict, cdict_frac)

cs_all, cs_fracs_all = Aggregator(), Aggregator()
cs_all2, cs_fracs_all2 = Aggregator(), Aggregator()

for diry in dirs:
  directory = os.path.join('data/dependency_graphs', diry, str(n))
  print directory
  
  # # Generate Graphs for Itemset Occurrences
  # for filename in glob.iglob(directory+'/itemset_occurrences/*.txt'):
  #   with open(filename, 'r') as f:
  #     iset = json.loads(f.read())
  #     print iset['itemset']
  #     xy_list = [(i,float(x)) for i, x in enumerate(iset['occurrences'])]
  #     other_xy_lists = [[(i, float(x)) for i, x in enumerate(xs)] for xs in iset['items'].itervalues()]
  #     DistributionPlot.scatter_plot(filename.rsplit(".", 1)[0], xy_list, other_xy_lists=other_xy_lists, sliding_window=10, title=str(iset['itemset']))
  
  cs, cs_fracs = conflict_graph(directory, "all_conflicts")
  cs_all.add(cs) # Generate stuff for average
  cs_fracs_all.add(cs_fracs)
  
  cs, cs_fracs = conflict_graph(directory, "all_conflicts_itemsets")
  cs_all2.add(cs) # Generate stuff for average
  cs_fracs_all2.add(cs_fracs)
  
BasicPlot.plot_twoscales("data/dependency_graphs/conflicts_all", [cs_all.avg(), cs_fracs_all.avg()], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps'])
BasicPlot.plot_twoscales("data/dependency_graphs/conflicts_all_itemsets", [cs_all2.avg(), cs_fracs_all2.avg()], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps'])

# Convert SVGs to PNGs
import subprocess
for diry in dirs:
  directory = os.path.join('data/dependency_graphs', diry, str(n))
  print directory
  p = subprocess.Popen("mogrify -density 144 -format png %s/*.svg" % directory,shell=True)
  out,err = p.communicate()