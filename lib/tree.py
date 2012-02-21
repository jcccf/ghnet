from misc import *
import pprint, json
pp = pprint.PrettyPrinter(indent=4)
from dateutil import parser as dtparser
from dateutil.relativedelta import *

db = MDb.MDb('ghnet', host='localhost', username='ghnet', password='ghnet87')
    
def file_history(filename='actionpack/lib/action_dispatch/http/mime_type.rb'):
  for sha, json_data, in db.q('SELECT sha, json FROM commits_detailed WHERE gname=\'rails\' ORDER BY commit_date ASC'):
    data = json.loads(json_data)
    # if filename in json_data:
    #   pp.pprint(json_data)
    for f in data['files']:
      if f['filename'] == filename:
        print f['filename'], f['status'], f['blob_url']
        
# file_history()
# 
# file_history('actionpack/lib/action_controller/mime_type.rb')
# 
# Update Rails
for sha, json_data, in db.q('SELECT sha, json FROM commits_detailed WHERE gname=\'rails\''):
  data = json.loads(json_data)
  db.q('UPDATE commits_detailed SET commit_date = %s WHERE sha = %s', (data['commit']['committer']['date'], sha))