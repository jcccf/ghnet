# encoding=utf-8
require 'set'
require 'csv'

class Node
  attr_reader :label, :ins, :outs, :undirs
  
  def initialize(label)
    @label = label
    @ins, @outs, @undirs = Set.new, Set.new, Set.new
  end
  
  def edge_to(node)
    @outs.add node
  end
  
  def edge_from(node)
    @ins.add node
  end
  
  def edge(node)
    @undirs.add node
  end
  
  def to_s
    return @label
  end
  
end

class NodeDict
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
      csv << ['n1', 'dir', 'n2']
      nodes.each do |k, v|
        v.undirs.each { |neighbor| csv << [v.label, "<>", neighbor] }
        v.ins.each { |neighbor| csv << [v.label, "<-", neighbor] }
        v.outs.each { |neighbor| csv << [v.label, "->", neighbor] }
      end    
    end
  end
  
end

# a = Node.new("hello")
# a.edge_to(Node.new("bye"))
# puts a.outs.size