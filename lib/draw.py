from misc import *
from plot import *
import json, datetime, time
from dateutil import parser as dtparser
from dateutil.relativedelta import *
import calendar
from collections import defaultdict, Counter
db = MDb.MDb('ghnet', host='localhost', username='ghnet', password='ghnet87')

def commit_weekdays(login, name):
  weekdays = []
  commit_lists = db.commits.where(glogin=login, gname=name)
  for glogin, gname, gno, json_data, created_at in commit_lists:
    try:
      data = json.loads(json_data)
    except Exception:
      print json_data
    for d in data:
      date = dtparser.parse(d['commit']['author']['date']) # "%Y-%m-%dT%H:%M:%S%Z"
      weekdays.append(date.weekday())
      # f.write('%s\n' % d['commit']['author']['date'].replace('T', ' ').rsplit('-', 1)[0])
  return weekdays
  
def commit_weekdays_all():
  weekdays_all, labels = [], []
  uniques = db.q('SELECT DISTINCT glogin, gname FROM commits WHERE gname <> "cakephp" AND gname <> "linux-2.6" AND gname <> "symfony" AND gname <> "TrinityCore" AND gname <> "zf2" ORDER BY created_at ASC')
  for glogin, gname in uniques:
    weekdays_all.append(commit_weekdays(glogin, gname))
    labels.append(gname)
  DistributionPlot.frequency_plots('data/plots/commits_over_a_week.png', weekdays_all, normalize=True, labels=labels, title="Proportion of commits throughout the week")

def contributor_dates(login, name):
  tuples = []
  weekdays = []
  commit_lists = db.commits.where(glogin=login, gname=name)
  for glogin, gname, gno, json_data, created_at in commit_lists:
    try:
      data = json.loads(json_data)
    except Exception:
      print json_data
    for d in data:
      date = dtparser.parse(d['commit']['author']['date'].split('T')[0]) # "%Y-%m-%dT%H:%M:%S%Z"
      tuples.append((d['commit']['author']['name'], date))
  # Convert list of tuples into dictionary
  dik = {}
  for auth, date in tuples:
    dik.setdefault(auth, []).append(date)
  # if len([1 for v in dik.iteritems() if len(v) >= 50]) > 10:
  #   dik = {k:v for k, v in dik.iteritems() if len(v) >= 50}
  # elif len([1 for v in dik.iteritems() if len(v) >= 10]) > 10:
  #   dik = {k:v for k, v in dik.iteritems() if len(v) >= 10}
  dik2 = sorted(sorted(dik.iteritems(), key=lambda x: len(x[1]), reverse=True)[:50])
  dicty = zip(*dik2)
  return dicty

def contributor_dates_all():
  uniques = db.q('SELECT DISTINCT glogin, gname FROM commits WHERE gname <> "cakephp" AND gname <> "linux-2.6" AND gname <> "symfony" AND gname <> "TrinityCore" AND gname <> "zf2" ORDER BY created_at ASC')
  for glogin, gname in uniques:
    print gname
    labels, dates = contributor_dates(glogin, gname)
    DistributionPlot.frequency_plots('data/plots/commits_over_time_per_contributor/%s.png' % gname, dates, labels=labels, title="# of commits by contributors over time")  

def commit_days(login, name, group_by='day'):
  days = []
  commit_lists = db.commits.where(glogin=login, gname=name)
  for glogin, gname, gno, json_data, created_at in commit_lists:
    try:
      data = json.loads(json_data)
    except Exception:
      print json_data
    for d in data:
      date = dtparser.parse(d['commit']['author']['date'].split('T')[0]) # "%Y-%m-%dT%H:%M:%S%Z"
      if group_by == 'day':
        days.append(date)
      elif group_by == 'week':
        days.append(date+relativedelta(weekday=MO(-1)))
      elif group_by == 'month':
        days.append(date+relativedelta(days=-date.day))
      # f.write('%s\n' % d['commit']['author']['date'].replace('T', ' ').rsplit('-', 1)[0])
  return days 

def commit_days_all():
  uniques = db.q('SELECT DISTINCT glogin, gname FROM commits WHERE gname <> "cakephp" AND gname <> "linux-2.6" AND gname <> "symfony" AND gname <> "TrinityCore" AND gname <> "zf2" ORDER BY created_at ASC')
  for glogin, gname in uniques:
    print gname
    days = commit_days(glogin, gname)
    DistributionPlot.frequency_plots('data/plots/commits_over_time/%s.png' % gname, [days], labels=[gname], title="# of commits over time")  
    days = commit_days(glogin, gname, group_by='week')
    DistributionPlot.frequency_plots('data/plots/commits_over_time/%s_week.png' % gname, [days], labels=[gname], title="# of commits over time")  
    days = commit_days(glogin, gname, group_by='month')
    DistributionPlot.frequency_plots('data/plots/commits_over_time/%s_month.png' % gname, [days], labels=[gname], title="# of commits over time")  

def commits_per_contributor(login, name, group_by='day'):
  days = []
  commit_lists = db.commits.where(glogin=login, gname=name)
  dik = defaultdict(int)
  for glogin, gname, gno, json_data, created_at in commit_lists:
    try:
      data = json.loads(json_data)
    except Exception:
      print json_data
    for d in data:
      dik[d['commit']['author']['name']] += 1
      # f.write('%s\n' % d['commit']['author']['date'].replace('T', ' ').rsplit('-', 1)[0])
  #print Counter(dik.values())
  BasicPlot.plot_loglog('data/plots/commits_per_contributor/%s.png' % gname, Counter(dik.values()), xlabel='Log Commits', ylabel='Log Contributors', title="# of contributors vs. # of commits")  

def commits_per_contributor_all():
  uniques = db.q('SELECT DISTINCT glogin, gname FROM commits WHERE gname <> "cakephp" AND gname <> "linux-2.6" AND gname <> "symfony" AND gname <> "TrinityCore" AND gname <> "zf2" ORDER BY created_at ASC')
  for glogin, gname in uniques:
    print gname
    commits_per_contributor(glogin, gname)

def commits_per_repo():
  uniques = db.q('SELECT DISTINCT glogin, gname FROM commits WHERE gname <> "cakephp" AND gname <> "linux-2.6" AND gname <> "symfony" AND gname <> "TrinityCore" AND gname <> "zf2" ORDER BY created_at ASC')
  commit_counts = []
  for login, name in uniques:
    count = 0
    commit_lists = db.commits.where(glogin=login, gname=name)
    for glogin, gname, gno, json_data, created_at in commit_lists:
      try:
        data = json.loads(json_data)
      except Exception:
        print json_data
      for d in data:
        count += 1
    commit_counts.append(count / 10)
  print Counter(commit_counts)
  BasicPlot.plot_loglog('data/plots/commits_per_repo.png', Counter(commit_counts), xlabel='Log Commits', ylabel='Log Repos', title="# of Repos vs. # of commits")  

def wfi_per_repo():
  '''Watchers, Forks and Open Issues per Repository'''
  watcher_counts, fork_counts, issue_counts = [], [], []
  repos = db.repos.all()
  for glogin, gname, json_data, created_at in repos:
    try:
      data = json.loads(json_data)
    except Exception:
      print json_data
    watcher_counts.append(int(data['watchers']))
    fork_counts.append(int(data['forks']))
    issue_counts.append(int(data['open_issues']))
  BasicPlot.plot_loglog('data/plots/watchers_per_repo.png', Counter(watcher_counts), xlabel='Log Watchers', ylabel='Log Repos', title="# of Repos vs. # of Watchers")  
  BasicPlot.plot_loglog('data/plots/forks_per_repo.png', Counter(fork_counts), xlabel='Log Forks', ylabel='Log Repos', title="# of Repos vs. # of Forks")  
  BasicPlot.plot_loglog('data/plots/issues_per_repo.png', Counter(issue_counts), xlabel='Log Open Issues', ylabel='Log Repos', title="# of Repos vs. # of Open Issues")    

# contributor_dates_all()
# commit_weekdays_all()
# commit_days_all()
# commits_per_contributor_all()
# commits_per_repo()
# wfi_per_repo()
# MGraph.draw_fork_trees(db)