from misc import *
from plot import *
import os, csv

dirs = [name for name in os.listdir('data/dependency_graphs') if os.path.isdir(os.path.join('data/dependency_graphs', name))]

cs_all, cs_fracs_all = {}, {}

for diry in dirs:
  directory = os.path.join('data/dependency_graphs', diry)
  print directory
  cdict, cdict_frac, i = {}, {}, 1
  with open(directory+"/200/conflicts.txt", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      print row['conflicts'], row['dig_remaining']
      cdict[i] = int(row['conflicts'])
      cdict_frac[i] = float(row['conflicts'])/float(row['dig_remaining']) if float(row['dig_remaining']) > 0 else 0
      i += 1
  BasicPlot.plot_twoscales("%s/200/conflicts" % directory, [cdict, cdict_frac], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps'])
  
  # Generate stuff for average (note that this graph is NOT reversed)
  cs = [v for k, v in sorted(cdict.items(), key=lambda x:x[0])]
  cs_fracs = [v for k, v in sorted(cdict_frac.items(), key=lambda x:x[0])]
  cs.reverse()
  cs_fracs.reverse()
  for i, c in enumerate(cs):
    cs_all.setdefault(i, []).append(c)
  for i, c in enumerate(cs_fracs):
    cs_fracs_all.setdefault(i, []).append(c)
  
cs_all = {k: sum(v)/len(v) for k, v in cs_all.iteritems()}
cs_fracs_all = {k: sum(v)/len(v) for k, v in cs_fracs_all.iteritems()}
BasicPlot.plot_twoscales("data/dependency_graphs/conflicts_all", [cs_all, cs_fracs_all], xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=['Conflicts', 'Conflicts/Deps'])