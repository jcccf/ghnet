# encoding=utf-8
require 'set'
require 'csv'
require 'json'
require_relative 'mcollections'

class MGraph
  
  # "Private" definition of Node
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
      return @label.to_s
    end
  
    include Comparable
    def <=>(other)
      self.label <=> other.label
    end
  end
  
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
  
  # Add a/an (weighted) directed edge from node i to node j 
  def dedge(i, j, weight=1)
    inode = (nodes[i] ||= Node.new(i))
    jnode = (nodes[j] ||= Node.new(j))
    inode.edge_to(jnode, weight)
    jnode.edge_from(inode, weight)
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
  def to_file(filename, keyencoder = nil)
    CSV.open(filename, 'wb') do |csv|
      csv << ['n1', 'dir', 'n2', 'w']
      nodes.each do |k, v|
        if keyencoder.nil?
          v.undirs.each { |neighbor,w| csv << [v, "<>", neighbor, w] if neighbor >= v }
          # v.ins.each { |neighbor,w| csv << [v.label, "<-", neighbor, w] }
          v.outs.each { |neighbor,w| csv << [v, "->", neighbor, w] }
        else
          v.undirs.each { |neighbor,w| csv << [keyencoder.encode(v.label), "<>", keyencoder.encode(neighbor.label), w] if neighbor >= v }
          # v.ins.each { |neighbor,w| csv << [keyencoder.encode(v.label), "<-", keyencoder.encode(neighbor.label), w] }
          v.outs.each { |neighbor,w| csv << [keyencoder.encode(v.label), "->", keyencoder.encode(neighbor.label), w] }
        end
      end    
    end
  end
  
end

def decode_mgraph_csv(source_filename, dest_filename, keyencoder)
  CSV.open(dest_filename, 'wb') do |csv|
    rows = CSV.read(source_filename)
    csv << rows.shift
    rows.each do |row|
      csv << [keyencoder.decode(row[0].to_i), row[1], keyencoder.decode(row[2].to_i), row[3]]
    end
  end
end

# a = Node.new("hello")
# a.edge_to(Node.new("bye"))
# puts a.outs.size