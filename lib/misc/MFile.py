def read_login_name(filename):
  '''Read files with /login/name format on each line'''
  repos = []
  with open(filename, 'r') as f:
    for l in f:
      repos.append(l.strip()[1:].split('/'))
  return repos