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
        db.forks.insert(glogin=login, gname=name, gno=num, parent_glogin=p_login, parent_gname=p_name, json=json.dumps(data), root_gname=root)
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
        db.commits.insert(glogin=login, gname=name, gno=num, json=json.dumps(data))
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

# seed_forks('data/popular_forked_20120206.txt')
# fork_tree()

# seed_commits('data/popular_forked_20120206.txt')
commits()