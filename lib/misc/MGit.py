import commands, os, unidecode, re
import cStringIO as StringIO
from dateutil import parser as dtparser
from dateutil.relativedelta import *

class MPatch:
  def __init__(self, sha):
    self.sha = sha
    self.patches = []
    self.is_rename = False
    
  def set_author(self, author, email):
    self.author = author
    self.email = email
  
  def set_date(self, datestring):
    self.date = dtparser.parse(datestring)
    
  def add_patch(self, a_start, a_end, b_start, b_end, lines):
    self.patches.append((a_start, a_end, b_start, b_end, lines))
  
  def set_index(self, a, b):
    self.index_a = a
    self.index_b = b

class MPatchPlayer:
  def __init__(self):
    self.lines = []
    self.commits = {}
    self.seen = {}
    
  # def _match_lines(self, lines, given_line_no):
  #   for i in range(0, len(self.lines)):
  #     found = True
  #     for j in range(0, len(lines)):
  #       if self.lines[i+j][1] != lines[j]:
  #         found = False
  #         break
  #       print j
  #     if found:
  #       return i - given_line_no
  #   return None
    
  def apply(self, patch_obj):
    if patch_obj.is_rename is True:
      print "Patch is a rename so doing nothing"
      return
    
    offset = 0
    self.commits[patch_obj.sha] = (patch_obj.author, patch_obj.email, patch_obj.date)
    for a_start, a_end, b_start, b_end, lines in patch_obj.patches:
      
      # Check if a patch has been applied before
      hashy = str(a_start + a_end + b_start + b_end) + ''.join([x+y for x,y in lines])
      if hashy in self.seen:
        print "Warning: Seen a patch in %s before" % patch_obj.sha
        offset += b_end - a_end
        continue
      else:
        self.seen[hashy] = True
      
      # Load newlines and oldlines
      newlines = [(patch_obj.sha, y) for x,y in lines if x != '-']
      oldlines = [y for x,y in lines if x != '+']
      
      # Basic Assertions
      try:
        assert len(newlines) == b_end
        assert len(oldlines) == a_end
      except AssertionError:
        print "Length of Oldlines/Newlines != a/b_end"
        raise Exception

      # Split original lines into parts to replace
      lines_before, lines_replacing, lines_after = self.lines[:a_start-1+offset], self.lines[a_start-1+offset:a_start+a_end-1+offset], self.lines[a_start+a_end-1+offset:]
      
      # Make sure what's being replaced exactly matches the patch
      for l1, (_,l2) in zip(oldlines, lines_replacing):
        if l1 != l2:
          print "Lines being replaced don't match!"
          print patch_obj.sha
          for l in oldlines:
            print l
          self.pp(lines_replacing)
          raise Exception
      
      # Update line and offset
      self.lines = lines_before + newlines + lines_after
      offset += b_end - a_end
  
  def pp(self, lines=None):
    if lines is None:
      lines = self.lines
    print "---"
    for sha, line in lines:
      print line
    print "---"

class MGit:
  def __init__(self, repo_directory):
    self.repo_directory = repo_directory
    os.chdir(repo_directory)
    
    self.commit_re = re.compile('^commit ([a-z0-9]+)$') # commit sha
    self.author_re = re.compile('^Author: ([a-zA-Z0-9\(\)\. \+\/]+) <([a-zA-Z0-9@.\-\+]+)>$') # Author: Asd <email>
    self.date_re = re.compile('^Date:(.+ [+-]{1}[0-9]{4})$') # Date: ???
    self.diff_re = re.compile('^diff --git a/([\w\/\.]+) b/([\w\/\.]+)$') # diff --git a/somefile b/somefile
    self.index_re = re.compile('^index ([a-z0-9]+)..([a-z0-9]+)[ ]*[0-9]*$') # index 0abc..0def 100644
    self.patch_re = re.compile('^@@ -([0-9]+),([0-9]+) \+([0-9]+),([0-9]+) @@.*$') # @@ -123,4 +123,5 @@
    
    self.patches = []
    
  def history(self, filename):
    res = commands.getoutput('git --no-pager log --follow -p %s' % filename)
    res = unidecode.unidecode(res)
    s = StringIO.StringIO(res)
    
    # Split into commit blocks
    commits, commit = [], []
    for l in s:
      l = l.rstrip()
      if self.commit_re.match(l):
        commits.append(commit)
        commit = [l]
      else:
        commit.append(l)
    commits.append(commit)
    commits.pop(0)
    for commit in commits:
      self.patches.append(self.parse_commit(commit))
    self.patches.reverse()
    path = self._patch_path()
    print len(path)
    player = MPatchPlayer()
    for patch in path:
      player.apply(patch)

  def _build_path(self, next):
    if next in self.adjacencies:
      max_val, max_path = 0, []
      for adj in self.adjacencies[next]:
        val, path = self._build_path(adj)
        if val > max_val:
          max_val, max_path = val, path
      return (max_val + 1, [self.patch_dict[next]] + max_path)
    else:
      return (1, [self.patch_dict[next]])

  def _patch_path(self):
    self.adjacencies, self.patch_dict, path = {}, {}, []
    for patch in self.patches:
      if patch.is_rename is False:
        self.adjacencies.setdefault(patch.index_a, []).append(patch.index_b)
        self.patch_dict[patch.index_b] = patch
    path = self._build_path(self.patches[0].index_b)[1]
    return path

  def parse_commit(self, lines):
    patch, mode = None, 'commit'
    for l in lines:
      if mode == 'commit':
        m = self.commit_re.match(l)
        if m:
          patch = MPatch(m.groups()[0])
          mode = 'author'
      elif mode == 'author':
        m = self.author_re.match(l)
        if m:
          patch.set_author(m.groups()[0], m.groups()[1])
          mode = 'date'
      elif mode == 'date':
        m = self.date_re.match(l)
        if m:
          patch.set_date(m.groups()[0])
          mode = 'index'
      elif mode == 'index':
        m = self.index_re.match(l)
        if m:
          patch.set_index(m.groups()[0], m.groups()[1])
          mode = 'patch_start'
      elif mode == 'patch_start':
        m = self.patch_re.match(l)
        if m:
          a_start, a_end, b_start, b_end = [int(x) for x in m.groups()]
          b_left = b_end
          patch_lines = []
          mode = 'patch_continue'
      elif mode == 'patch_continue':
        m = self.patch_re.match(l)
        if m:
          patch.add_patch(a_start, a_end, b_start, b_end, patch_lines)
          a_start, a_end, b_start, b_end = [int(x) for x in m.groups()]
          b_left = b_end
          patch_lines = []
        elif b_left > 0:
          b_left -= 1
          if len(l) > 0:
            if l != '\\ No newline at end of file':
              patch_lines.append((l[0],l[1:]))
              if l[0] == '-':
                b_left += 1
            else:
              b_left += 1
          else:
            patch_lines.append(('', ''))

    if 'similarity index 100%' in lines:
      patch.is_rename = True
    else:
      patch.add_patch(a_start, a_end, b_start, b_end, patch_lines)
    return patch

git = MGit('../rails')
git.history('actionpack/lib/action_dispatch/http/mime_types.rb')