import urllib, urllib2, json, pprint, time

class RateLimitError(Exception):
  pass

class NotFoundError(Exception):
  pass

class NoneError(Exception):
  pass

class GithubScraper:
  
  def __init__(self, username="ghnet", password="ghnet78"):
    # passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    #     passman.add_password(realm=None, uri="https://api.github.com", user=username, passwd=password)
    #     auth_handler = urllib2.HTTPBasicAuthHandler(passman)
    #     opener = urllib2.build_opener(auth_handler)
    #     urllib2.install_opener(opener)
    self.headers = None # Headers from the last request
    self.last_request = None # The last request made
    self.RATE_MIN, self.SLEEP_TIME = 100, 3600
    
  def header_value(self, name):
    if self.headers:
      for header in self.headers:
        if name in header:
          return header.split(':', 1)[1].strip()
    return None
    
  def ratelimit_remaining(self):
    if self.header_value('X-RateLimit-Remaining'):
      return int(self.header_value('X-RateLimit-Remaining'))
    else:
      return 999999
    
  def request(self, url):
    if self.ratelimit_remaining() < self.RATE_MIN:
      print "Sleeping for %d seconds..." % self.SLEEP_TIME
      time.sleep(self.SLEEP_TIME)
      raise RateLimitError(self.ratelimit_remaining())
    try:
      time.sleep(1)
      print "Getting... %s" % url
      if "https://" in url:
        fil = urllib.urlopen(url)
      else:
        req = urllib2.Request('https://api.github.com/%s' % url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')
        fil = urllib2.urlopen(req)
      self.headers = fil.info().headers
      self.last_request = url
      return json.loads(fil.read())
    except urllib2.HTTPError as err:
      print "HTTPError | %s | %s" % (url, err)
      if "404" in str(err):
        raise NotFoundError()
      else:
        raise NoneError()
  
  def multipage_request(self, url):
    yield self.request(url)
    while True:
      if self.header_value('Link'):
        has_next = False
        rels = self.header_value('Link').split(",")
        for r in rels:
          parts = r.split(";")
          if "next" in parts[1]:
            next_url = parts[0].strip()[1:-1]
            next_return = self.request(next_url)
            yield next_return
            has_next = True
        if not has_next:
          break
      else:
        break
  
  #
  # Convenience Methods
  #
    
  def own_repositories(self):
    return self.multipage_request('user/repos')
    
  def repo(self, user, repo):
    return self.request('repos/%s/%s' % (user, repo))
    
  def repo_collaborators(self, user, repo):
    return self.multipage_request('repos/%s/%s/collaborators' % (user, repo))
    
  def repo_watchers(self, user, repo):
    return self.multipage_request('repos/%s/%s/watchers' % (user, repo))
    
  def repo_commits(self, user, repo):
    return self.multipage_request('repos/%s/%s/commits' % (user, repo))
    
  def repo_forks(self, user, repo):
    return self.multipage_request('repos/%s/%s/forks' % (user, repo))
    
  def repo_pull_requests(self, user, repo):
    return self.multipage_request('repos/%s/%s/pulls' % (user, repo))
    
  def repo_issues(self, user, repo):
    return self.multipage_request('repos/%s/%s/issues' % (user, repo))
    
  def repo_issue_comments(self, user, repo, id):
    return self.multipage_request('repos/%s/%s/issues/%s/comments' % (user, repo, id))
    
  def repo_issue_events(self, user, repo, id):
    return self.multipage_request('repos/%s/%s/issues/%s/events' % (user, repo, id))