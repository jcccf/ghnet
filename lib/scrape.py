from misc import *
import pprint, json
pp = pprint.PrettyPrinter(indent=4)

# db = MDb.MDb('ghnet', host='localhost', username='ghnet', password='ghnet87')
db = MDb.MDb('memo')
db_queue = MDb.MDbQueue(db)
g = GithubScraper.GithubScraper()

#
# Scrape Forks
#

def fork_tree():
  while True:
    deq = db_queue.dq('forks')
    if deq is None:
      break
    idd, (login, name, p_login, p_name, root) = deq
    try:
      for num, data in enumerate(g.repo_forks(login, name)):
        if db.forks.insert(glogin=login, gname=name, gno=num, parent_glogin=p_login, parent_gname=p_name, json=json.dumps(data), root_gname=root) == -2:
          break
        for d in data:
          if d['owner'] is not None and d['name'] is not None:
            db_queue.q('forks', (d['owner']['login'], d['name'], login, name, root))
      db.commit()
      db_queue.dq_end(idd)
    except GithubScraper.NotFoundError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.NoneError as err: # Other random error
      db_queue.dq_rollback(idd)

def seed_forks(filename):
  repos, parent_repos = [], []
  # Read in file
  with open(filename, 'r') as f:
    for l in f:
      repos.append(l.strip()[1:].split('/'))
  # Traverse each up to parent
  for glogin, gname in repos:
    while True:
      d = g.repo(glogin, gname)
      if d['fork'] is True:
        glogin, gname = d['parent']['owner']['login'], d['parent']['name']
      else:
        break
    parent_repos.append((glogin, gname))
  print parent_repos
  # Populate queue
  for glogin, gname in parent_repos:
    db_queue.q('forks', (glogin, gname, None, None, gname)) # Last gname is the root
  db.commit()

#
# Seeding
#

def seed(type, filename):
  repos = MFile.read_login_name(filename)
  for glogin, gname in repos:
    db_queue.q(type, (glogin, gname))
  db.commit()

def seed_commits(filename):
  seed('commits')
  
def seed_repos(filename):
  seed('repos', filename)

def seed_issues(filename):
  seed('issues', filename)
  
def seed_pull_requests(filename):
  seed('pulls', filename)

#
# Scraping
#
def issues():
  while True:
    deq = db_queue.dq('issues')
    if deq is None:
      break
    idd, (login, name) = deq
    try:
      for num, data in enumerate(g.repo_issues(login, name, 'open')):
        if db.issues.insert(glogin=login, gname=name, gno=num, json=json.dumps(data), is_open=1) == -2:
          break
      db.commit()
      for num, data in enumerate(g.repo_issues(login, name, 'closed')):
        if db.issues.insert(glogin=login, gname=name, gno=num, json=json.dumps(data), is_open=0) == -2:
          break
      db.commit()
      db_queue.dq_end(idd)
    except GithubScraper.NotFoundError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.GoneError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.NoneError as err: # Other random error
      db_queue.dq_rollback(idd)

def seed_issues_detailed(filename):
  repos = MFile.read_login_name(filename)
  for login, name in repos:
    issue_lists = db.issues.where(glogin=login, gname=name)
    for glogin, gname, gno, is_open, json_data, created_at in issue_lists:
      data = json.loads(json_data)
      for d in data:
        db_queue.q('issues_d', (glogin, gname, d['number']))
    db.commit()
    
def issues_detailed():
  while True:
    deq = db_queue.dq('issues_d')
    if deq is None:
      break
    idd, (login, name, number) = deq
    try:
      data = g.repo_issue(login, name, number)
      if data['pull_request'] is None or data['pull_request']['patch_url'] is None:
        is_pull_request = 0
      else:
        is_pull_request = 1
      db.issues_detailed.insert(glogin=login, gname=name, gnum=number, state=data['state'], is_pull_request=is_pull_request, issue_date=data['created_at'], json=json.dumps(data))
      for num, data in enumerate(g.repo_issue_comments(login, name, number)):
        if db.issues_comments.insert(glogin=login, gname=name, gnum=number, gno=num, json=json.dumps(data)) == -2:
          break
      for num, data in enumerate(g.repo_issue_events(login, name, number)):
        if db.issues_events.insert(glogin=login, gname=name, gnum=number, gno=num, json=json.dumps(data)) == -2:
          break
      db.commit()
      db_queue.dq_end(idd)
    except GithubScraper.NotFoundError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.NoneError as err: # Other random error
      db_queue.dq_rollback(idd)

def pull_requests():
  while True:
    deq = db_queue.dq('pulls')
    if deq is None:
      break
    idd, (login, name) = deq
    try:
      for num, data in enumerate(g.repo_pull_requests(login, name, 'open')):
        if db.pull_requests.insert(glogin=login, gname=name, gno=num, json=json.dumps(data), is_open=1) == -2:
          break
      db.commit()
      for num, data in enumerate(g.repo_pull_requests(login, name, 'closed')):
        if db.pull_requests.insert(glogin=login, gname=name, gno=num, json=json.dumps(data), is_open=0) == -2:
          break
      db.commit()
      db_queue.dq_end(idd)
    except GithubScraper.NotFoundError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.GoneError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.NoneError as err: # Other random error
      db_queue.dq_rollback(idd)

def commits():
  while True:
    deq = db_queue.dq('commits')
    if deq is None:
      break
    idd, (login, name) = deq
    try:
      for num, data in enumerate(g.repo_commits(login, name)):
        if db.commits.insert(glogin=login, gname=name, gno=num, json=json.dumps(data)) == -2:
          break
      db.commit()
      db_queue.dq_end(idd)
    except GithubScraper.NotFoundError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.NoneError as err: # Other random error
      db_queue.dq_rollback(idd)

def repos():
  while True:
    deq = db_queue.dq('repos')
    if deq is None:
      break
    idd, (login, name) = deq
    try:
      data = g.repo(login, name)
      db.repos.insert(glogin=login, gname=name, json=json.dumps(data))
      db.commit()
      db_queue.dq_end(idd)
    except GithubScraper.NotFoundError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.NoneError as err: # Other random error
      db_queue.dq_rollback(idd)

def seed_commits_detailed(login, name):
  commit_lists = db.commits.where(glogin=login, gname=name)
  for glogin, gname, gno, json_data, created_at in commit_lists:
    data = json.loads(json_data)
    for d in data:
      db_queue.q('commits_d', (glogin, gname, d['sha'], d['url']))
  db.commit()
  
def seed_rails():
  '''Redo invalid commit logs'''
  with open('data/rails_commits.txt', 'r') as f:
    for l in f:
      sha = l.replace('\n', '').strip()
      db.q('DELETE FROM commits_detailed WHERE sha=%s', sha)
      db_queue.q('commits_d', ('rails', 'rails', sha, "https://api.github.com/repos/rails/rails/commits/%s" % sha))
  db.commit()
  
def commits_detailed():
  while True:
    deq = db_queue.dq('commits_d')
    if deq is None:
      break
    idd, (login, name, sha, url) = deq
    try:
      data = g.request(url)
      db.commits_detailed.insert(glogin=login, gname=name, sha=sha, commit_date=data['commit']['committer']['date'], json=json.dumps(data))
      db.commit()
      db_queue.dq_end(idd)
    except GithubScraper.NotFoundError as err: # 404 File Not Found
      db_queue.dq_skip(idd)
    except GithubScraper.NoneError as err: # Other random error
      db_queue.dq_rollback(idd)

# seed_forks('data/popular_forked_20120206.txt')
# fork_tree()
# seed_commits('data/popular_forked_redo.txt')
# commits()
# seed_repos('data/popular_forked_redo.txt')
# repos()
# seed_issues('data/popular_forked_20120206.txt')
# issues()
# seed_pull_requests('data/popular_forked_20120206.txt')
# pull_requests()
# seed_issues_detailed('data/popular_forked_20120206.txt')
issues_detailed()

# seed_repos('data/popular_watched_20120206.txt')
# repos()
# seed_forks('data/popular_watched_20120206.txt')
# fork_tree()
# seed_commits('data/popular_watched_20120206.txt')
# commits()

# seed_repos('data/interesting_20120206.txt')
# repos()
# seed_forks('data/interesting_20120206.txt')
# fork_tree()
# seed_commits('data/interesting_20120206.txt')
# commits()

# seed_commits_detailed('rails', 'rails') 
# commits_detailed() # Still undone