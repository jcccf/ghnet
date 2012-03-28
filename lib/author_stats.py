from misc import *
import json, unidecode, csv

db = MDb.MDb('ghnet', host='localhost', username='ghnet', password='ghnet87')
# db = MDb.MDb('memo')

class AuthorStat:
  def __init__(self):
    self.commit_count = 0
    self.merge_pull_request_count = 0
    self.bug_count = 0
    self.lines_added = 0
    self.lines_deleted = 0
    self.lines_modified = 0
    
    self.created_files = set()
    self.files = set()

def unique_committers(glogin, gname):
  committers = {}
  commits = db.commits.where(glogin=glogin, gname=gname)
  for glogin, gname, gno, json_data, created_at in commits:
    data = json.loads(json_data)
    for commit in data:
      committer = (commit['commit']['committer']['name'], commit['commit']['committer']['email'])
      if not committer in committers:
        committers[committer] = AuthorStat()
      committers[committer].commit_count += 1
      commit_message = commit['commit']['message'].lower()
      if "merge" in commit_message: # "Merge pull request"
        committers[committer].merge_pull_request_count += 1
      if "bug" in commit_message or "fix" in commit_message:
        committers[committer].bug_count += 1
        
  # Load detailed file stats
  commits = db.commits_detailed.where(glogin=glogin, gname=gname)
  for glogin, gname, sha, commit_date, json_data, created_at in commits:
    data = json.loads(json_data)
    committer = (data['commit']['committer']['name'], data['commit']['committer']['email'])
    if not committer in committers:
      committers[committer] = AuthorStat()
    committers[committer].lines_added += data['stats']['additions']
    committers[committer].lines_deleted += data['stats']['deletions']
    committers[committer].lines_modified += data['stats']['total']
    for file_data in data['files']:
      committers[committer].files.add(file_data['filename'])
  
  with open("data/first_authors.txt", "r") as f:
    reader = csv.reader(f)
    for row in reader:
      ffn, fname, femail = row
      for name, email in committers.keys():
        if femail == email:
          committers[(name, email)].created_files.add(ffn)
        
  for (name, email), stats in committers.iteritems():
    print "%s, %d, %d, %d, %d, %d, %d" % (unidecode.unidecode(name), stats.commit_count, stats.merge_pull_request_count, stats.bug_count, stats.lines_modified, len(stats.files), len(stats.created_files))
    

unique_committers('rails', 'rails')