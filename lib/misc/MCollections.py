# MCollections
import operator

# Given a list of (index,value) lists, output a (index,avg_value) list
# For example, [[(0,1),(1,2),(2,3)], [(0,4),(1,5)], [(0,7)]] gives [4.0, 3.5, 3]
def lists_mean(lists):
  list_cum = {}
  for listy in lists:
    for i, v in listy:
      list_cum.setdefault(i, []).append(v)
  list_cum = [ (i, float(sum(v))/len(v)) for i, v in sorted(list_cum.iteritems(), key=operator.itemgetter(0))]
  return list_cum

# Given a list of list of numbers, output the lists with indices, and also output the average
# For example, [[1,2,3], [4,5], [7]] gives [(0, 4.0), (1, 3.5), (2, 3)] and [[(0,1),(1,2),(2,3)], [(0,4),(1,5)], [(0,7)]]
def index_and_average(lists):
  listnew = []
  for listy in lists:
    listnew.append([(i,x) for i, x in enumerate(listy)])
  listavg = lists_mean(listnew)
  return (listavg, listnew)
  
# Given a list of numbers, return a cumulative list instead
# For example, [1, 3, 4] gives [1, 4, 8] (unnormalized) or [0.125, 0.5, 1.0] (normalized)
def cumulative(listy, normalized=True):
  cumulative_list, count = [], 0.0
  for l in listy:
    count += l
    cumulative_list.append(count)
  if normalized:
    cumulative_list = [c/count for c in cumulative_list]
  return cumulative_list
  
# Given a list of lists, return lists of tuples of (index, value)
# For example, [[1,2], [3]] gives [[(0,1), (1,2)], [(0,3)]]
def countify(lists, start_index=None):
  if start_index is None:
    return [[(i,x) for i,x in enumerate(listy)] for listy in lists]
  else:
    return [[(i+start_index,x) for i,x in enumerate(listy)] for listy in lists]
  
if __name__ == '__main__':
  b = [[(0,1),(1,2),(2,3)], [(0,4),(1,5)], [(0,7)]]
  print lists_mean(b)
  
  a = [[1,2,3], [4,5], [7]]
  print index_and_average(a)
  
  a =  [1,3,4]
  print cumulative(a)
  
  print countify([a])