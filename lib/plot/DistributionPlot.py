import matplotlib
import matplotlib.pyplot as plt
import operator
from collections import Counter

def colors(length):
  colors=[]
  c = matplotlib.cm.get_cmap('gist_rainbow')
  for i in range(length):
    colors.append(c(1.*i/length))
  return colors

def histogram_plot(filename, xs, bins=1, normed=1, color='b', label='hello', ylim=None, xlim=None, xlabel=None, ylabel=None, histtype='stepfilled'):
  plt.clf()
  plt.figure().set_size_inches(20,10)
  n, bins, patches = plt.hist(xs, bins, normed=normed, histtype=histtype, rwidth=0.8, color=color, label=label)
  if xlabel:
    plt.xlabel(xlabel)
  if ylabel:
    plt.ylabel(ylabel)
  if ylim:
    plt.ylim(ylim)
  if xlim:
    plt.xlim(xlim)
  plt.legend()
  plt.savefig('%s' % filename)
  return (n, bins, patches)
  
def frequency_plots(filename, xs_list, normalize=False, color='b', labels=['Plot1'], title=None, ylim=None, xlim=None, xlabel=None, ylabel=None):
  '''Take lists of lists of values, create multiple frequency tables and plot multiple lines'''
  ccolors = colors(len(xs_list))
  plt.clf()
  plt.figure().set_size_inches(25,15)
  ax = plt.subplot(111)
  for i, xs in enumerate(xs_list):
    dik = Counter(xs)
    if normalize:
      diksum = sum(dik.values())
      dik = {k:float(v)/diksum for k,v in dik.iteritems()}
    dicty = zip(*sorted(dik.iteritems()))
    ax.plot(dicty[0], dicty[1], color=ccolors[i], label=labels[i])
    ax.scatter(max(dik, key=dik.get), dik[max(dik, key=dik.get)], color=ccolors[i])
  if xlabel:
    ax.xlabel(xlabel)
  if ylabel:
    ax.ylabel(ylabel)
  if ylim:
    plt.ylim(ylim)
  else:
    plt.ylim(ymin=0)
  if xlim:
    plt.xlim(xlim)
  if title:
    plt.title(title)
  box = ax.get_position()
  ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])  
  from matplotlib.font_manager import FontProperties
  fontP = FontProperties()
  fontP.set_size('small')
  ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop=fontP)
  plt.savefig('%s' % filename)
