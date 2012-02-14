from misc import *
from plot import *
import json, datetime, time
from dateutil import parser as dtparser
from dateutil.relativedelta import *
import calendar
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
  DistributionPlot.frequency_plots('data/plots/commits_over_a_week.png', weekdays_all, labels=labels, title="Proportion of commits throughout the week")

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

# contributor_dates_all()
# commit_weekdays_all()
# commit_days_all()
MGraph.draw_fork_trees(db)