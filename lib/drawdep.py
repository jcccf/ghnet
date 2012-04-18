from misc import *
from plot import *
import os, csv, glob, json

n = 200

dirs = [name for name in os.listdir('data/dependency_graphs') if os.path.isdir(os.path.join('data/dependency_graphs', name))]

cs_all, cs_fracs_all = {}, {}

for diry in dirs:
  directory = os.path.join('data/dependency_graphs', diry, str(n))
  print directory
  
  # Generate Graphs for Itemset Occurrences
  for filename in glob.iglob(directory+'/itemset_occurrences/*.txt'):
    with open(filename, 'r') as f:
      iset = json.loads(f.read())
      print iset['itemset']
      xy_list = [(i,float(x)) for i, x in enumerate(iset['occurrences'])]
      other_xy_lists = [[(i, float(x)) for i, x in enumerate(xs)] for xs in iset['items'].itervalues()]
      DistributionPlot.scatter_plot(filename.rsplit(".", 1)[0], xy_list, other_xy_lists=other_xy_lists, sliding_window=10, title=str(iset['itemset']))
  
  # Generate basic conflict count
  cdict, cdict_frac, i = {}, {}, 1
  with open(directory+"/all_conflicts.txt", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      print row['conflicts'], row['dig_remaining']
      cdict[i] = float(row['conflicts'])
      cdict_frac[i] = float(row['conflicts'])/float(row['dig_remaining']) if float(row['dig_remaining']) > 0 else 0
      i += 1
  BasicPlot.plot_twoscales("%s/all_conflicts" % directory, [cdict, cdict_frac], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps'])
  
  # Generate stuff for average
  cs = [v for k, v in sorted(cdict.items(), key=lambda x:x[0])]
  cs_fracs = [v for k, v in sorted(cdict_frac.items(), key=lambda x:x[0])]
  for i, c in enumerate(cs):
    cs_all.setdefault(i, []).append(c)
  for i, c in enumerate(cs_fracs):
    cs_fracs_all.setdefault(i, []).append(c)
  
cs_all = {k: sum(v)/len(v) for k, v in cs_all.iteritems()}
cs_fracs_all = {k: sum(v)/len(v) for k, v in cs_fracs_all.iteritems()}
BasicPlot.plot_twoscales("data/dependency_graphs/conflicts_all", [cs_all, cs_fracs_all], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps'])