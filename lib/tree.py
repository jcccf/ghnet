from misc import *
from plot import *
import pprint, json, os, csv, StringIO
pp = pprint.PrettyPrinter(indent=4)
from dateutil import parser as dtparser
from dateutil.relativedelta import *
import re

def walk_and_prepare():
  is_image_file = re.compile('^.*(\.(jpg|jpeg|png|gif))$')

  with open('data/first_authors.txt', 'w') as fa:
    fa_writer = csv.writer(fa)
    
    # Attempt a walk
    with open('data/graphs/file_hist/a.txt', 'w') as f:
      git = MGit.MGit('../rails')
      for path, subdirs, files in os.walk('.'):
        for name in files:
          filename = os.path.join(path, name)[2:]
          
          if filename[:5] == '.git/' or is_image_file.match(filename) is not None:
            continue
          print filename
          player = git.history(filename)
          if filename[0] == '.':
            filename = '0' + filename
          os.chdir('../ghnet')
          if player is not None:
            fa_writer.writerow([filename, player.patches[0].author, player.patches[0].email])
            graph, info = MGraph.draw_lineage(player.lineage, filename)
          
            # Get all paths in a file
            paths = MGraph.paths_to_leaves(graph, sort_paths=True)
            max_path_len = paths[0][0] if paths is not None else 0
          
            f.write('%d %d %d %d %d %d %d %d %s\n' % (info['nodes'], info['edges'], info['diameter'], info['height'], player.total_seconds(), len(player.authors(unique=True)), len(player.patches), max_path_len, filename))
          os.chdir('../rails')  

def walk():
  is_image_file = re.compile('^.*(\.(jpg|jpeg|png|gif))$')    
  # Attempt a walk
  git = MGit.MGit('../rails')
  for filepath, subdirs, files in os.walk('.'):
    for name in files:
      filename = os.path.join(filepath, name)[2:]    
      # filename = "actionmailer/lib/action_mailer.rb"
      if filename[:5] == '.git/' or is_image_file.match(filename) is not None:
        continue
      print filename
      
      player = git.history(filename)
      if filename[0] == '.':
        filename = '0' + filename
      os.chdir('../ghnet')
      if player is not None:
        graph, info = MGraph.draw_lineage(player.lineage, filename)
          
        # Get all paths in a file
        paths = MGraph.paths_to_leaves(graph, sort_paths=True)

        # # Auth Activity Plots
        # os.chdir('../ghnet')
        # fauths = authors_from_file(player)
        # authors, activities = MList.tuples_to_kvlists(auth)
        # DistributionPlot.activity_plot('data/plots/author_activities_file/%s.png' % filename.replace('/', '|'), activities, authors)
            
        # Individual Path Activity Plots
        auths = authors_from_paths(player, paths)
        # for auth in auths:
        #   authors, activities = MList.tuples_to_kvlists(auth)
        #   DistributionPlot.activity_plot('hellx.png', activities, authors) # TODO Fix this

        # TODO Looking at changes in a file
        # for path in paths:
        #   if max_consecutive_deletes(player, path) > 3:
        #     print_lines(player, path)
        
        with open('data/oneline_changes/%s.txt' % filename.replace('/','|'), 'w') as f:
          for path in paths:
            for group in filter_consecutive_add_deletes(player, path):
              f.write(print_lines(player, path, group, to_string=True))
              f.write('  \n')
        
      os.chdir('../rails')
                        
    #   break
    # break

def authors_from_paths(player, paths):
  '''Get a list of authors responsible for commits on this path'''
  authors = []
  for num, groups in paths:
    authors.append([(player.patches[i].author, player.patches[i].date) for i, s, e in groups])
  return authors

def filter_consecutive_add_deletes(player, path, add_limit=1, del_limit=1, equality=True):
  length, pathy = path
  groups, group = [], []
  for i, s, e in pathy:
    add_count = len([l for l in player.lineage[i] if l == (s,e)])
    del_count = len(player.deleted_hist[i])
    if equality is True:
      if add_limit == add_count and del_count == del_limit:
        group.append((i,s,e))
      elif len(group) > 0:
        groups.append(group)
        group = []
    else:
      if add_limit <= add_count and del_count <= del_limit:
        group.append((i,s,e))
      elif len(group) > 0:
        groups.append(group)
        group = []
  if len(group) > 0:
    groups.append(group)
    group = []
  return groups

def max_consecutive_deletes(player, path):
  '''Return the maximum number of consecutive commits in this path which have deletions'''
  length, pathy = path
  max_consec, curr = 0, 0
  for i, s, e in pathy:
    if len(player.deleted_hist[i]) > 0:
      curr += 1
      if curr > max_consec:
        max_consec = curr
    else:
      curr = 0
  return max_consec

def print_lines(player, path, group=None, to_string=False):
  '''Print the lines added and deleted on a path (or a defined path (confusingly called a group here))'''
  def subpath(pathy):
    if to_string is True:
      sio = StringIO.StringIO()
      for i, s, e in pathy:
        for j,l in enumerate(player.lineage[i]):
          if l == (s,e):
            sio.write("+ %s\n" % player.lines_hist[i][j][1][1])
        for l in player.deleted_hist[i]:
          sio.write("- %s\n" % l[1])
        sio.write("==\n")
      s = sio.getvalue()
      sio.close()
      return s
    else:
      for i, s, e in pathy:
        print ">>> Added:"
        for j,l in enumerate(player.lineage[i]):
          if l == (s,e):
            print player.lines_hist[i][j]
        if len(player.deleted_hist[i]) > 0:
          print ">>> Deleted:"
          for l in player.deleted_hist[i]:
            print l 
        print "---"
      print "==="

  if group is not None:
    return subpath(group)
  else:
    length, pathy = path
    print length, pathy
    # for patch in player.patches:
    #   for p in patch.patches:
    #     for l in p[4]:
    #       print l
    #     print "---"
    #   print "==="
    # for i,lin in enumerate(player.lineage):
    #   print i, lin
    return subpath(pathy)
        
def plot():
  num_nodes, num_edges, num_diameters, num_seconds, num_heights, num_commits, num_authors = [], [], [], [], [], [] ,[]
  with open('data/graphs/file_hist/a.txt', 'r') as f:
    for l in f:
      l = l.rstrip()
      # print l
      nodes, edges, diameter, height, seconds, authors, commits, longest_path, filename = l.split(' ', 8)
      num_seconds.append(int(seconds)/86400)
      num_nodes.append(int(nodes))
      num_edges.append(int(edges))
      num_diameters.append(int(diameter))
      num_heights.append(int(height))
      num_commits.append(int(commits))
      num_authors.append(int(authors))
  print "Scatter Plots..."
  DistributionPlot.scatter_plot('data/plots/file_hist/nodes_diameter.png', zip(num_diameters, num_nodes))
  DistributionPlot.scatter_plot('data/plots/file_hist/nodes_heights.png', zip(num_heights, num_nodes))
  DistributionPlot.scatter_plot('data/plots/file_hist/nodes_age.png', zip(num_seconds, num_nodes))
  DistributionPlot.scatter_plot('data/plots/file_hist/diameter_age.png', zip(num_seconds, num_diameters))
  DistributionPlot.scatter_plot('data/plots/file_hist/height_age.png', zip(num_seconds, num_heights))
  print "Distribution Plots..."
  DistributionPlot.histogram_plot('data/plots/file_hist/nodes_dist.png', num_nodes, bins=100)
  DistributionPlot.histogram_plot('data/plots/file_hist/edges_dist.png', num_edges, bins=100)
  DistributionPlot.histogram_plot('data/plots/file_hist/diameters_dist.png', num_diameters, bins=100)
  DistributionPlot.histogram_plot('data/plots/file_hist/seconds_dist.png', num_seconds, bins=100)
  DistributionPlot.histogram_plot('data/plots/file_hist/heights_dist.png', num_heights, bins=100)
  DistributionPlot.histogram_plot('data/plots/file_hist/commits_dist.png', num_commits, bins=100)
  DistributionPlot.histogram_plot('data/plots/file_hist/authors_dist.png', num_authors, bins=100)

def test():
  test_files = ['actionpack/lib/action_dispatch/http/mime_type.rb', 
    'actionmailer/lib/action_mailer/mail_helper.rb',
    'actionmailer/test/fixtures/auto_layout_mailer/hello.html.erb',
    'actionpack/lib/action_view/helpers/asset_tag_helper.rb',
    'actionpack/lib/action_view/template/resolver.rb',
    'actionpack/test/controller/controller_fixtures/app/controllers/user_controller.rb',
    'actionpack/test/controller/new_base/render_layout_test.rb',
    'actionpack/test/fixtures/public/javascripts/application.js',
    'activesupport/lib/active_support/core_ext/file.rb',
    'activesupport/lib/active_support/core_ext/object/inclusion.rb']

  git = MGit.MGit('../rails')    
  for test in test_files:
    print '---'
    print test
    player = git.history(test)
    os.chdir('../ghnet')
    if player is not None:
      graph = MGraph.draw_lineage(player.lineage, test)
    os.chdir('../rails')
  # player = git.history('actionmailer/test/fixtures/attachments/foo.jpg')   # Will fail for sure

#test()  
# walk()
# walk_and_prepare()
plot()