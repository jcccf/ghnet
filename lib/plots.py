from misc import *
from plot import *
import os, csv, glob, json, itertools

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
  def __init__(self, conflict_name='fq', base_name='dir', n='200'):
    self.conflict_name = conflict_name
    self.base_name = base_name
    self.n = n
    self.cs_all = Aggregator()
    self.cs_fracs_all = Aggregator()
    
  def generate_and_add(self, directory):
    # Generate # of Conflicts
    cs, cs_fracs = conflict_graph(os.path.join(directory, "%s_%s" % (self.conflict_name, self.base_name)), "all_conflicts_%s_%s" % (self.conflict_name, self.base_name))
    self.cs_all.add(cs) # Generate stuff for average
    self.cs_fracs_all.add(cs_fracs)
    
  def plot_agg(self):
    BasicPlot.plot_twoscales("data/dependency_graphs/all_conflicts_%s_%s_%s" % (self.conflict_name, self.base_name, self.n), [self.cs_all.avg(), self.cs_fracs_all.avg()], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps'])

# Generate Graphs for Pairs of Itemset Occurrences
# I.e. Fraction of commits with both A and B against commits containing A
# /reg does not renumber the commit sequence - i.e. there may be gaps in the plot
# /renum renumbers the commit sequence so that there are no gaps
def itemset_one_against_another(directory):
  # Generate Graphs for 1 against another
  for filename in glob.iglob(directory+'/itemset_occurrences/*.txt'):
    num = int(filename.rsplit("/", 1)[1].split(".", 1)[0])
    with open(filename, 'r') as f:
      iset = json.loads(f.read())
      # main_xy_list = [(i,float(x)) for i, x in enumerate(iset['occurrences'])]
      xy_lists, xy_lists_renumbered = [], []
      for i1, i2 in itertools.combinations(iset['items'].keys(), 2):
        try:
          # Find the one that comes first,
          i1list = [(i, float(x)) for i, x in enumerate(iset['items'][i1])]
          i2list = [(i, float(x)) for i, x in enumerate(iset['items'][i2])]
          i1exist = [(i,x) for i, x in i1list if x > 0]
          i2exist = [(i,x) for i, x in i2list if x > 0]
          i1min = min(i1exist, key=lambda x: x[0])[0]
          i2min = min(i2exist, key=lambda x: x[0])[0]
          if i1min > i2min: i1list, i2list, i1exist, i2exist = i2list, i1list, i2exist, i1exist
          # Generate the scatter plot
          i2exist = { i:x for i, x in i2exist } # turn i2exist into a hash
          xy_list = [(i, i2exist[i] if i in i2exist else 0) for i, _ in i1exist]
          xy_list_renumbered = [(j,x) for j, x in enumerate([x for i, x in xy_list])]
          xy_lists.append(xy_list)
          xy_lists_renumbered.append(xy_list_renumbered)
        except:
          print "Failed for ", num, iset['items'].keys(), i1, i2
      DistributionPlot.line_plots(directory+"/itemset_occurrences/reg/%d" % num, xy_lists, sliding_window=50, title=str(iset['itemset']))
      DistributionPlot.line_plots(directory+"/itemset_occurrences/renum/%d" % num, xy_lists_renumbered, sliding_window=10, title=str(iset['itemset']))

# Generate Graphs for Itemset Occurrences
def itemset_occurrences(directory):
  for filename in glob.iglob(directory+'/itemset_occurrences/*.txt'):
    with open(filename, 'r') as f:
      iset = json.loads(f.read())
      print iset['itemset']
      xy_list = [(i,float(x)) for i, x in enumerate(iset['occurrences'])]
      other_xy_lists = [[(i, float(x)) for i, x in enumerate(xs)] for xs in iset['items'].itervalues()]
      DistributionPlot.scatter_plot(filename.rsplit(".", 1)[0], xy_list, other_xy_lists=other_xy_lists, sliding_window=10, title=str(iset['itemset']))

# Generate graph of # of unique Authors + # of Frequent Itemsets (/edges)
def auth_edges(directory):
  authors, frequent_edges = {}, {}
  for filename in glob.iglob(directory+"/af_*.txt"):
    i = int(filename.rsplit("af_", 1)[1].split(".")[0])
    with open(filename, 'r') as f:
      af = json.loads(f.read())
      authors[i] = len(af)
    g = MNode.csv_to_graph(directory+"/fq_%d.txt" % i)
    frequent_edges[i] = len(g.edges())
  print authors, frequent_edges
  BasicPlot.plot_twoscales(directory+"/auth_fq/auth_fq_%s_%s" % (diry, str(n)), [authors, frequent_edges], labels=["Authors", "# of Frequent Itemset Edges"])

def make_directories(directory):
  for d in ['auth_fq', 'itemset_occurrences/renum', 'itemset_occurrences/reg']:
    out_dir = os.path.join(directory, d)
    if not os.path.exists(out_dir):
      os.makedirs(out_dir)

if __name__ == '__main__':
  n = "200"

  dirs = [name for name in os.listdir('data/dependency_graphs') if os.path.isdir(os.path.join('data/dependency_graphs', name))]
  
  fqdir = ConflictGraphAggregator('fq', 'dir', n)
  fqdep = ConflictGraphAggregator('fq', 'dep', n)
  fcdep = ConflictGraphAggregator('fc', 'dep', n)
  for diry in dirs:
    directory = os.path.join('data/dependency_graphs', diry, str(n))
    print directory
    make_directories(directory)
  
    # Occurrences of itemsets in the commit history and individual occurrences
    # itemset_occurrences(directory)

    print "Graph of frac. of commits containing B against commits containing A..."
    itemset_one_against_another(directory)
  
    print "Unique Authors + Frequent Itemset Edges"
    auth_edges(directory)
    
    print "Conflict Graphs over Time"
    fqdir.generate_and_add(directory)
    fqdep.generate_and_add(directory)
    fcdep.generate_and_add(directory)
  
  fqdir.plot_agg()
  fqdep.plot_agg()
  fcdep.plot_agg()