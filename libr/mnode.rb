# encoding=utf-8
require 'set'
require 'csv'

class Node
  attr_reader :label, :ins, :outs, :undirs
  
  def initialize(label)
    @label = label
    @ins, @outs, @undirs = {}, {}, {}
  end
  
  def edge_to(node, weight = 1)
    @outs[node] = weight
  end
  
  def edge_from(node, weight = 1)
    @ins[node] = weight
  end
  
  def edge(node, weight = 1)
    @undirs[node] = weight
  end
  
  def edge_inc(node)
    @undirs[node] ||= 0
    @undirs[node] += 1
  end
  
  def to_s
    return @label
  end
  
  include Comparable
  def <=>(other)
    self.label <=> other.label
  end
end

class MGraph
  attr_accessor :nodes
  
  def initialize(nodes=nil)
    @nodes = nodes.nil? ? {} : nodes
  end
  
  def [](k)
    nodes[k]
  end
  
  def []=(k, v)
    nodes[k] = v
  end
  
  # Add a/an (weighted) undirected edge from Node i to Node j
  def edge(i, j, weight=1)
    inode = (nodes[i] ||= Node.new(i))
    jnode = (nodes[j] ||= Node.new(j))
    inode.edge(jnode, weight)
    jnode.edge(inode, weight)
  end
  
  # Add an undirected edge from Node i to Node j, incrementing the weight of the edge if it exists
  def edge_inc(i, j)
    inode = (nodes[i] ||= Node.new(i))
    jnode = (nodes[j] ||= Node.new(j))
    inode.edge_inc(jnode)
    jnode.edge_inc(inode)
  end
  
  def each
    nodes.each { |node| yield node }
  end
  
  def to_s
    nodes.each do |k, v|
      puts v
      v.undirs.each do |neighbor|
        puts "\t %s" % neighbor
      end
    end
  end
  
  # Outputs list of edges to a file (CSV)
  def to_file(filename)
    CSV.open(filename, 'wb') do |csv|
      csv << ['n1', 'dir', 'n2', 'w']
      nodes.each do |k, v|
        v.undirs.each { |neighbor,w| csv << [v.label, "<>", neighbor, w] if neighbor >= v }
        v.ins.each { |neighbor,w| csv << [v.label, "<-", neighbor, w] }
        v.outs.each { |neighbor,w| csv << [v.label, "->", neighbor, w] }
      end    
    end
  end
  
end

# a = Node.new("hello")
# a.edge_to(Node.new("bye"))
# puts a.outs.size