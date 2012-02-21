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
# Scrape Commits
#

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
      
def seed_commits(filename):
  repos = MFile.read_login_name(filename)
  for glogin, gname in repos:
    db_queue.q('commits', (glogin, gname))
  db.commit()
  
def seed_repos(filename):
  repos = MFile.read_login_name(filename)
  for glogin, gname in repos:
    db_queue.q('repos', (glogin, gname))
  db.commit()
  
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
commits_detailed() # Still undone