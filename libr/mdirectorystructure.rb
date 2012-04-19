# encoding=utf-8
require_relative 'mnode'
require_relative 'mfile'
require 'pathname'
require 'set'

# Returns the directory structure of this directory as a graph and output it to filename
def directory_graph(directory, filename)
  g = MGraph.new
  chdir_return(directory) do
    Dir.glob("**/*").each do |f|
      # Link each file to its parent
      parent_dir = Pathname.new(f).parent.to_s
      g[f] ||= Node.new(f)
      g[parent_dir] ||= Node.new(f)
      g[parent_dir].edge_to(g[f])
    end
  end
  g.to_file(filename)
end

if __FILE__ == $0
  
end