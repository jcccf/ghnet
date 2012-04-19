require 'json'
require 'set'
require 'iconv'
require_relative 'mnode'
require_relative 'mfile'

# Read in commit JSONs from MNode's repo_all_commits
class MCommits
  
  include Enumerable
  
  def initialize(filename, commits_per_block=200, yield_remainder=true)
    @commits_per_block = commits_per_block
    @yield_remainder = yield_remainder
    File.open(filename, 'rb') { |f| @commits = JSON.parse(f.read) }
  end
  
  # Yield commits in blocks of commits_per_block
  def each
    n = @commits.size / @commits_per_block
    remainder = @commits.size - n * @commits_per_block
    n.times do |i|
      start_index, end_index = i*@commits_per_block, (i+1)*@commits_per_block-1
      # -(i+1)*@commits_per_block, -(i*@commits_per_block + 1)
      yield @commits[start_index..end_index]
    end
    if @yield_remainder && remainder > 0
      start_index, end_index = n*@commits_per_block, n*@commits_per_block + remainder - 1
      yield @commits[start_index, end_index]
    end
  end
  
  # Return the number of blocks that will be yielded for each
  def num_blocks
    n = @commits.size / @commits_per_block
    n += 1 if @yield_remainder && n * @commits_per_block < @commits.size
    n
  end
  
  # Return an array of all commits
  def all_commits
    # ac = []
    # self.each do |commits|
    #   ac += commits
    # end
    # ac
    @commits
  end
  
end

# Generate graph where nodes are files, edges are commits
def files_commits_graph(commits, filename)
  g = MGraph.new
  commits.each do |commit|
    commit['paths'].combination(2).each do |i, j|
      g.edge_inc(i, j)
    end
  end
  g.to_file(filename)
end

# Generate graph where nodes are authors, edges are files (modified in commits by the author)
# Weights are # of common files between authors
def authors_files_graph(commits, filename)
  pathlist = {}
  commits.each do |commit|
    auth = parse_name(commit['author'])
    commit['paths'].each do |path|
      pathlist[path] ||= Set.new
      pathlist[path] << auth
    end
  end
  g = MGraph.new
  pathlist.each do |_,auths|
    auths.to_a.combination(2).each do |i, j|
      g.edge_inc(i, j)
    end
  end
  g.to_file(filename)
end

# Generate graph where cliques are frequent files commonly modified together (itemsets)
# Edge weight is the frequency of that itemset
def file_commits_itemsets(commits, filename, json_filename)
  pathlists = commits.map { |commit| commit['paths'] }.compact
  itemsets = nil
  chdir_return('../../..') do
    itemsets = frequent_itemsets(pathlists, 3, 2)
  end
  
  # Write Itemsets to JSON
  File.open(json_filename, 'w') do |f|
    f.write(JSON.generate(itemsets))
  end
        
  # Identify frequent itemsets in each pathlist, and add paths, then output
  g = MGraph.new
  itemsets.each do |itemset, freq|
    itemset.combination(2).each do |i1, i2|
      g.edge(i1, i2, freq)
    end
  end
  g.to_file(filename)
end

# Generate a list of 0s or 1s depending on whether an itemset is present in a commit
def itemset_occurrences(commits, itemset, filename)
  itemset_set = Set.new(itemset)
  item_occurrences = {}
  itemset.each { |item| item_occurrences[item] = [] }
  pathlists = commits.map { |commit| Set.new(commit['paths']) }
  x, xcommits = [], []
  pathlists.each_with_index do |pathlist, i|
    if itemset_set.subset? pathlist
      x << 1
      paths = Iconv.iconv('utf-8', 'iso8859-1', *commits[i]['paths'])
      xcommits << { :sha => commits[i]['sha'], :message => Iconv.iconv('utf-8', 'iso8859-1', commits[i]['message']).first, :pathlist => paths, :related_files => commits[i]['related_files'] }
    else
      x << 0
    end
    itemset.each do |item|
      item_occurrences[item] << ((pathlist.include? item) ? 1 : 0)
    end
  end
  File.open(filename, 'w') do |f|
    f.write(JSON.generate({ :itemset => itemset, :occurrences => x, :items => item_occurrences, :commits => xcommits }))
  end
end

# Given a list of commits, a directory of frequent itemsets, and a threshold,
# output all occurrences for each itemset of the (threshold) most frequent itemsets
def all_itemset_occurrences(commits_file, directory, threshold=0.1)
  puts "Generating itemset occurrences with Threshold %f..." % threshold
  all_commits = MCommits.new(commits_file, 200, true).all_commits
  
  frequencies = Hash.new(0)
  chdir_return(directory) do 
    # Get frequencies from each json frequency file
    Dir.glob("json_fq_*.txt").each do |filename|
      File.open(filename, 'r') do |f|
        json = JSON.parse f.read
        json.each do |itemset, frequency|
          frequencies[itemset] += frequency
        end
      end
    end
    
    # Sort in descending frequency order
    frequencies = frequencies.to_a.sort { |x,y| y[1] <=> x[1] }
    frequencies = frequencies[0..(threshold * frequencies.size)]
  
    # Generate occurrence file for each itemset
    Dir.mkdir('itemset_occurrences') if not File.exist? 'itemset_occurrences'
    i = 0
    frequencies.each do |itemset, frequency|
      itemset_occurrences(all_commits, itemset, "itemset_occurrences/%d.txt" % i)
      i += 1
    end
  end
end

if __FILE__ == $0
  # mc = MCommits.new('data/commits_all/diaspora.txt', 200, true)  
  # a = Set.new
  # mc.each do |commits|
  #   puts commits.size
  #   commits.each do |commit|
  #     a << commit['sha']
  #   end
  #   # files_commits_graph(commits, 'test.txt')
  # end
  # puts "Total Set Size: %d" % a.size
  # puts mc.all_commits
  
  # all_commits = []
  # mc.each do |commits|
  #   all_commits += commits
  # end
  # itemset_occurrences(all_commits, ["cloud-crowd.gemspec", "lib/cloud-crowd.rb"], "test.txt")
  
  all_itemset_occurrences('data/commits_all/cloud-crowd.txt', "data/dependency_graphs/cloud-crowd/200")
end