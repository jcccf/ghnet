import commands, os, unidecode, re
import cStringIO as StringIO
from dateutil import parser as dtparser
from dateutil.relativedelta import *

class MPatch:
  '''A collection of patches'''
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
  '''Plays MPatches in sequence'''
  def __init__(self):
    self.lines = []
    self.commits = {}
    self.seen = {}
    self.lineage = [] # lineage of lines in a file, with same indexing as patches
    # the lineage is a list of numbers or tuples, where a tuple appears if a particular line of a particular patch was
    # "influenced" by the lines indicated in the tuple from the previous patch
    # If not, a line will have a number which is the index of the corresponding line in the previous patch
    self.patches = [] # list of patches applied
    self.lines_hist = [] # file history, with same indexing as patches
    self.deleted_hist = [] # deleted lines history, with same indexing as patches
    
  def _match_lines(self, lines, given_line_no):
    for i in range(0, len(self.lines)):
      found = True
      for j in range(0, len(lines)):
        if self.lines[i+j][1] != lines[j]:
          found = False
          break
        # print j
      if found:
        return i - given_line_no
    return None
    
  def total_seconds(self):
    if len(self.patches) > 0:
      return (self.patches[-1].date - self.patches[0].date).total_seconds()
    else:
      return 0
      
  def authors(self, unique=False):
    if unique is True:
      return set([patch.author for patch in self.patches])
    else:
      return [(patch.author, patch.date) for patch in self.patches]
    
  def apply(self, patch_obj):
    # self.pp()
    if patch_obj.is_rename is True:
      print "Patch is a rename so doing nothing"
      return
    
    offset = 0
    if len(self.lineage) > 0:
      new_level = [i for i in range(0, len(self.lineage[-1]))]
    else:
      new_level = []

    self.commits[patch_obj.sha] = (patch_obj.author, patch_obj.email, patch_obj.date)
    for a_start, a_end, b_start, b_end, lines in patch_obj.patches:
      
      # Check if a patch has been applied before
      hashy = str(a_start + a_end + b_start + b_end) + ''.join([x+y for x,y in lines])
      if hashy in self.seen:
        print "Warning: Seen a patch in %s before" % patch_obj.sha
        # print self.seen[hashy]
        checklines = [y for x,y in lines if x != '-']
        if self._match_lines(checklines, 0) is not None:
          print "Changes from this patch exists in the current file"
          offset += b_end - a_end
          continue
        else:
          print "Changes don't exist - maybe patch was reverted?"
      else:
        self.seen[hashy] = lines
      
      # Load newlines and oldlines
      self.lines = [(sha, ('',y)) for sha,(x,y) in self.lines] # Reset + markers so that they don't carry over patches
      newlines = [(patch_obj.sha, (x,y)) for x,y in lines if x != '-'] # Set sha and + marker (if it exists) for each line
      oldlines = [y for x,y in lines if x != '+']
      deletedlines = [(a_start-1+d,y) for d,(x,y) in enumerate(lines) if x == '-'] # Keep a record of deleted lines
      
      # Basic Assertions
      try:
        assert len(newlines) == b_end
        assert len(oldlines) == a_end
      except AssertionError:
        print "Length of Oldlines/Newlines != a/b_end"
        print patch_obj.sha
        print a_end, b_end
        print newlines
        print oldlines
        print lines
        raise Exception

      # Split original lines into parts to replace
      lines_before, lines_replacing, lines_after = self.lines[:a_start-1+offset], self.lines[a_start-1+offset:a_start+a_end-1+offset], self.lines[a_start+a_end-1+offset:]
      
      # Make sure what's being replaced exactly matches the patch
      for l1, (_,(x,l2)) in zip(oldlines, lines_replacing):
        if l1 != l2:
          print "Lines being replaced don't match!"
          print a_start, a_end, b_start, b_end
          print patch_obj.sha
          for l in oldlines:
            print l
          self.pp(lines_replacing)
          raise Exception
      
      # Generate Lineage
      # Limit change area to the boundaries of + and - on both sides of the patch
      x1, x2 = 0, 0
      if len(lines) > 0:
        while lines[x1][0] != '-' and lines[x1][0] != '+':
          x1 += 1
        while lines[-x2-1][0] != '-' and lines[-x2-1][0] != '+':
          x2 += 1
      
      # Extend "influence" by 1 line in each direction
      # Helps especially when a line was simply added, so that its parents are the line before and after
      new_start, new_end = a_start-1+x1, a_start-2+a_end-x2
      if new_start > 0:
        new_start -= 1
      if len(self.lineage) > 0 and new_end < len(self.lineage[-1]) - 1:
        new_end += 1
      new_level_portion = [(new_start, new_end)] * (b_end-x1-x2)
            
      # print a_start, a_end, b_start, b_end, x1, x2
      # print lines
      # print new_level_portion
      level_before, level_after = new_level[:a_start+x1-1+offset], new_level[a_start+a_end-x2-1+offset:]
      new_level = level_before + new_level_portion + level_after
      
      # Update line and offset
      self.lines = lines_before + newlines + lines_after
      offset += b_end - a_end

    # Add this patch to the patch list
    self.patches.append(patch_obj)    
    # Append new level to lineage
    self.lineage.append(new_level)
    # Add this version to the history
    self.lines_hist.append(list(self.lines))
    self.deleted_hist.append(deletedlines)
      
  def pp(self, lines=None):
    '''Pretty print current lines or given lines'''
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
    self.author_re = re.compile('^Author: ([a-zA-Z0-9\(\)\., \'!&\+\/-]+) <([a-zA-Z0-9_, @.\-\+]+)>$') # Author: Asd <email>
    self.date_re = re.compile('^Date:(.+ [+-]{1}[0-9]{4})$') # Date: ???
    self.diff_re = re.compile('^diff --git a/([\w\/_\.]+) b/([\w\/_\.]+)$') # diff --git a/somefile b/somefile
    self.index_re = re.compile('^index ([a-z0-9]+)..([a-z0-9]+)[ ]*[0-9]*$') # index 0abc..0def 100644
    self.patch_re = re.compile('^@@ -([0-9]+)(,([0-9]+))? \+([0-9]+)(,([0-9]+))? @@.*$') # @@ -123,4 +123,5 @@
    
    self.patches = []
    
  def history(self, filename):
    self.patches = []
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
      patch = self.parse_commit(commit)
      if patch is not None:
        self.patches.append(patch)
    self.patches.reverse()
    
    if len(commits) == 0:
      print "%s has 0 commits!" % filename
      return None

    path = self._patch_path()
    
    if path is None:
      return None
    
    print "Path Length:", len(path)
    for p in path:
      print p.sha
    player = MPatchPlayer()
    for patch in path:
      player.apply(patch)
    # for lin in player.lineage:
    #   print lin
    return player

  def _build_path(self, next, seen):
    # TODO Broken
    # How about maintain a next tuple which has sha
    max_len, max_path = 0, []
    if next in self.adjacencies:
      for adj in self.adjacencies[next]:
        if not adj in seen:
          length, path = self._build_path(adj, seen + [next])
          if length > max_len:
            max_val, max_path = length, path
      return (max_len + 1, [next] + max_path)
    else:
      return (0, [])

  def _patch_path(self):
    '''Generate the longest path through the given patches from the first patch, so that we can replay changes'''
    self.adjacencies, self.patch_dict, path = {}, {}, []
    for patch in self.patches:
      if patch.is_rename is False:
        self.adjacencies.setdefault(patch.index_a, []).append(patch.index_b)
        # if not patch.index_a in self.patch_dict:
        self.patch_dict.setdefault(patch.index_a, []).append(patch)
    path = self._build_path(self.patches[0].index_a, [])[1]
    
    if len(path) <= 1:
      "Path is too short!"
      return None
    
    # Convert path of indices into path of patch objects
    if path[-1] in self.adjacencies: # Add last patch object
      path.append(self.adjacencies[path[-1]][0])
    newpath = []
    
    # print self.adjacencies
    for i in range(0, len(path)-1):
      index_a, index_b = path[i], path[i+1]
      for patch in self.patch_dict[index_a]:
        if patch.index_b == index_b:
          newpath.append(patch)
          break
    path = newpath
    
    return path

  def parse_commit(self, lines):
    '''Parse a single commit when calling git diff'''
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
          patch_lines = []
          a_start, a_end, b_start, b_end = 0, 0, 0, 0
      elif mode == 'patch_start':
        m = self.patch_re.match(l)
        if m:
          a_start = int(m.groups()[0])
          a_end = 1 if m.groups()[2] is None else int(m.groups()[2])
          b_start = int(m.groups()[3])
          b_end = 1 if m.groups()[5] is None else int(m.groups()[5])
          b_left, a_left = b_end, a_end
          mode = 'patch_continue'
      elif mode == 'patch_continue':
        m = self.patch_re.match(l)
        if m:
          patch.add_patch(a_start, a_end, b_start, b_end, patch_lines)
          a_start = int(m.groups()[0])
          a_end = 1 if m.groups()[2] is None else int(m.groups()[2])
          b_start = int(m.groups()[3])
          b_end = 1 if m.groups()[5] is None else int(m.groups()[5])
          b_left, a_left = b_end, a_end
          patch_lines = []
        elif b_left > 0 or a_left > 0:
          b_left -= 1
          a_left -= 1
          if len(l) > 0:
            if l != '\\ No newline at end of file':
              patch_lines.append((l[0],l[1:]))
              if l[0] == '-':
                b_left += 1
              elif l[0] == '+':
                a_left += 1
            else:
              b_left += 1
              a_left += 1
          else:
            patch_lines.append(('', ''))
    if 'similarity index 100%' in lines:
      patch.is_rename = True
    else:
      try:
        if a_start == 0 and a_end == 0 and b_start == 0 and b_end == 0:
          print 'Warning - this diff has no patches'
        patch.add_patch(a_start, a_end, b_start, b_end, patch_lines)
      except UnboundLocalError:
        print "Warning, skipping this commit"
        print lines
        return None
    return patch

if __name__ == '__main__':
  git = MGit('../rails')
  player = git.history('actionpack/lib/action_dispatch/http/mime_type.rb')
  os.chdir('../ghnet')
  import MGraph
  MGraph.draw_lineage(player.lineage)