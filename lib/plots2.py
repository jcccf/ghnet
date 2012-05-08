# -*- coding: utf-8 -*-
import json, cPickle as pickle
from misc import *
from plot import *
from collections import Counter

# Graph of # of Total Line Edits vs Commits (per Author)
# Graph of # of Total Line Edits vs Commits (Avg)
def line_edits_to_commits(diry):
  with open('data/all_time/%s/author_add_del.txt' % diry, 'rb') as f:
    data = json.load(f)
  
  totals = []
  for author, changes in data.iteritems():
    totals.append([(i,x) for i, x in enumerate([c[2] for c in changes])])
  print [len(t) for t in totals]
  avg_totals = MCollections.lists_mean(totals)
  DistributionPlot.line_plots('data/all_time/%s/author_add_del.eps' % diry, totals, xy_main=avg_totals, scatter=False)

# Plot of the # of touched components vs commits
def components_in_commits(diry):
  with open('data/all_commits/%s.txt' % diry, 'rb') as f:
    commits = json.load(f)
  with open('data/all_time/%s/clusters/affinity.pickle' % diry, 'rb') as f:
    clusters = pickle.load(f)
    rev_clusters = {}
    for i, files in clusters.iteritems():
      for fil in files:
        rev_clusters[fil] = i
  counts = []
  for i, commit in enumerate(commits):
    clusters = set()
    for p in commit['paths']:
      if p in rev_clusters:
        clusters.add(rev_clusters[p])
    counts.append((i, len(clusters)))
  DistributionPlot.line_plots('data/all_time/%s/components_commits.eps' % diry, [counts], xlabel='Components over time', ylabel='# of touched components')
  
# Plot several metrics relating to components in commits by authors
def components_by_authors(diry):
  with open('data/all_commits/%s.txt' % diry, 'rb') as f:
    commits = json.load(f)
  with open('data/all_time/%s/clusters/affinity.pickle' % diry, 'rb') as f:
    clusters = pickle.load(f)
    rev_clusters = {}
    for i, files in clusters.iteritems():
      for fil in files:
        rev_clusters[fil] = i
        
  author_lists = {}
  author_lists_numtouched = {}
  author_lists_clusters, author_lists_clusters_count = {}, {}
  author_lists_all_clusters = {}
  for i, commit in enumerate(commits):
    author = commit['parsed_author']
    clusters = set()
    for p in commit['paths']:
      if p in rev_clusters:
        clusters.add(rev_clusters[p])
    for cluster in clusters:
      author_lists.setdefault(author, []).append((i, cluster))
    author_lists_numtouched.setdefault(author, []).append(len(clusters))
    author_lists_clusters.setdefault(author, set()).update(clusters)
    author_lists_clusters_count.setdefault(author, []).append(len(author_lists_clusters[author]))
    author_lists_all_clusters.setdefault(author, []).extend(clusters)
    
  # Plot touched components in a commit on the y-axis, over all commits, color-coded by author
  DistributionPlot.line_plots('data/all_time/%s/components_commits_authors.eps' % diry, author_lists.values(), lines=False, xlabel='Commits over time', ylabel='Component ID')
  
  # Print number of touched components over # of commits by an author
  author_lists_cum_mean, author_lists_cum = MCollections.index_and_average(author_lists_numtouched.values())
  DistributionPlot.line_plots('data/all_time/%s/numcomponents_commits_authors.eps' % diry, author_lists_cum, xy_main=author_lists_cum_mean, scatter=False, ylabel='# of touched components', xlabel='# of commits by an author')
  DistributionPlot.line_plots('data/all_time/%s/numcomponents_commits_authors_10.eps' % diry, author_lists_cum, xy_main=author_lists_cum_mean, scatter=False, ylabel='# of touched components', xlabel='# of commits by an author', xlim=[0,10])
  
  # Print cumulative total number of touched components for each author over # of commits by an author
  alcc_mean, alcc = MCollections.index_and_average(author_lists_clusters_count.values())
  DistributionPlot.line_plots('data/all_time/%s/cumcomponents_commits_authors.eps' % diry, alcc, xy_main=alcc_mean, scatter=False, ylabel='Cumulative # of touched components', xlabel='# of commits by an author')
  DistributionPlot.line_plots('data/all_time/%s/cumcomponents_commits_authors_10.eps' % diry, alcc, xy_main=alcc_mean, scatter=False, ylabel='Cumulative # of touched components', xlabel='# of commits by an author', xlim=[0,10])
  
  # Plot proportion of activity in first N components against # of components
  all_counts = []
  for _, clusters in author_lists_all_clusters.iteritems():
    c = Counter(clusters)
    counts = [v for k,v in sorted(c.iteritems(), key=lambda x:-x[1])]
    all_counts.append(MCollections.cumulative(counts))
  all_counts = MCollections.countify(all_counts, start_index=1)
  DistributionPlot.line_plots('data/all_time/%s/propactivity_components_authors.eps' % diry, all_counts, sliding_window=0, scatter=False, ylabel='% of activity in 1st N components', xlabel='N')
    

# Graph of # of components vs commits

if __name__ == '__main__':
  # line_edits_to_commits('cancan')
  # components_in_commits('cancan')
  components_by_authors('cancan')