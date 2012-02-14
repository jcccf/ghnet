import sqlite3, os.path, MySQLdb, time

class MDb(object):
  def __init__(self, database, host='lion.cs.cornell.edu', username='jc882', password='memo3330'):
    self.conn = MySQLdb.connect(host, username, password, database)
    self.conn.text_factory = str
    self.c = self.conn.cursor()

  class MDbTable():
    '''Helper class for ActiveRecord-style database access'''
    def __init__(self, mdb, table_name):
      self.mdb = mdb
      self.table_name = table_name
    def insert(self, **vals):
      snames, svals, stuple = '(', 'VALUES(', ()
      for k,v in vals.items():
        if v is not None:
          snames += k + ', '
          svals += '%s, '
          stuple += (v,)
      snames = snames[:-2] + ')'
      svals = svals[:-2] + ')'
      return self.mdb.q('INSERT INTO '+self.table_name+snames+' '+svals, stuple)
    def where(self, **vals):
      svals, stuple = ' WHERE ', ()
      for k,v in vals.items():
        if v is not None:
          svals += k + '=%s AND '
          stuple += (v,)
      svals = svals[:-5]
      return self.mdb.q('SELECT * FROM '+self.table_name+svals, stuple)
    def all(self):
      return self.mdb.q('SELECT * FROM %s' % self.table_name)
    
  def q(self, query, tuples=None):
    '''Make a database query and return all rows'''
    try:
      if tuples:
        self.c.execute(query, tuples)
      else:
        self.c.execute(query)
      return self.c.fetchall()
    except MySQLdb.IntegrityError as err:
      print "Integrity Error | %s" % err
      return -2
    
  def i(self, query, tuples=None):
    '''Make a database query and return the cursor (useful for iterating)'''
    if tuples:
      self.c.execute(query, tuples)
    else:
      self.c.execute(query)
    return self.c
    
  def __getattr__(self, name):
    if len(self.q('SHOW TABLES LIKE %s', name)) == 0:
      raise AttributeError(name)
    return MDb.MDbTable(self, name)
    
  def commit(self):
    self.conn.commit()
    
  def rollback(self):
    self.conn.rollback()
    
  def close(self):
    self.c.close()

import pickle

class MDbQueue:
  def __init__(self, mdb):
    self.mdb = mdb
    
  def q(self, key, value, commit=False):
    '''Queue something'''
    self.mdb.queues.insert(k=key, v=pickle.dumps(value))
    if commit is True:
      self.mdb.commit()
    
  def dq(self, key):
    '''Dequeue the first thing with the given key, and set it as being in use'''
    val = self.mdb.q("SELECT * FROM queues WHERE k='%s' AND in_use=0 ORDER BY id ASC LIMIT 1" % key)
    if len(val) == 0:
      return None
    self.mdb.q('UPDATE queues SET in_use = 1 WHERE id = %s', val[0][0])
    self.mdb.commit()
    return (val[0][0], pickle.loads(val[0][2])) # (id, value) tuple
    
  def dq_rollback(self, id):
    self.mdb.rollback()
    self.mdb.q('UPDATE queues SET in_use = 0 WHERE id = %s', id)
    self.mdb.commit()
    print "Rolled back id %d, sleeping for 30 minutes..." % id
    time.sleep(1800)
    
  def dq_skip(self, id):
    self.mdb.rollback()
    self.dq_end(id)
    print "Skipped over id %d..." % id
    
  def dq_end(self, id):
    '''Complete the dequeue by deleting the appropriate id'''
    self.mdb.q('DELETE FROM queues WHERE id = %s', id)
    self.mdb.commit()