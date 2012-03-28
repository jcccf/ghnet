'''List Manipulation Functions'''

def tuples_to_dictlist(tuples):
  '''Convert a list of (a,b) tuples into a dictionary of lists with (a) as the keys and (b) as the values in a list'''
  dicty = {}
  for a, b in tuples:
    dicty.setdefault(a, []).append(b)
  return dicty

def dict_to_kvlists(dicty):
  '''Separate a dictionary into a key list and value list with corresponding entries'''
  l1, l2 = [], []
  for k, v in dicty.iteritems():
    l1.append(k)
    l2.append(v)
  return (l1, l2)
  
def tuples_to_kvlists(tuples):
  '''Converts (a,b) tuples to a list of (a)s and a list of (b) lists'''
  return dict_to_kvlists(tuples_to_dictlist(tuples))
    
def dicts_to_dict(dictlist):
  '''Convert a list of dictionaries into a dictionary, with the new dictionary having keys as a union
  of the keys of the original dictionaries, and values in a list'''
  dicty = {}
  for d in dictlist:
    for k, v in d.iteritems():
      dicty.setdefault(k, []).append(v)
  return dicty
    
if __name__ == '__main__':
  td = tuples_to_dictlist([('a', 1), ('b', 1), ('a', 3)])
  print td
  print dict_to_twolists(td)