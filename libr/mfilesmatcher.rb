# encoding=utf-8
require_relative 'mnode'
require 'pathname'
require 'set'

class FilesMatcher
  attr_reader :filelist
  
  # List all files in a directory, and filter out only .rb files for now!
  def self.files_in_directory(dir='../rails', filter=['\.rb'])
    regexes = filter.map { |f| Regexp.new f + "$" }.compact
    curr = Dir.pwd
    Dir.chdir(dir)
    Dir.glob("**/*").each do |filename|
      regexes.each do |r|
        if filename =~ r
          yield filename
          break
        end
      end
    end
    Dir.chdir(curr)
  end
  
  def initialize(directory)
    @directory = directory
    @filelist = {}
    FilesMatcher.files_in_directory(directory) do |filename|
      @filelist[filename] = true
    end
  end
  
  # Open a file and read line by line
  def open_file(filename)
    curr = Dir.pwd
    Dir.chdir(@directory)
    File.open(filename, 'r') do |f|
      yield f
    end
    Dir.chdir(curr)
  end
  
  # Should return a list of lists, each list with the possible dependency files in sorted order of decreasing importance
  def probable_dependencies(filename)
    raise NotImplementedError
  end
  
  # Returns the top matches for each possible dependency and returns a list with no duplicates
  def dependencies(filename)
    Set.new(probable_dependencies(filename).find_all {|d| d.any? }.map {|d| d.first }).to_a
  end
  
  def dependency_graph_to_file(filename)
    nl = MGraph.new
    @filelist.each do |filename,v|
      nl[filename] ||= Node.new(filename)
      dependencies(filename).each do |dependent_file|
        nl[dependent_file] ||= Node.new(dependent_file)
        nl[filename].edge_to(nl[dependent_file])
      end
    end
    nl.to_file(filename)
  end

end

# Dependency Generator for Ruby Files
# Matches require and require_relative, and tries to resolve relative paths or makes a partial path match
# TODO autoload load include
class RubyFilesMatcher < FilesMatcher
    
  @@req_regex = /[\s]*require(_relative)?[\s]*[\'\"]{1}(\#\{[a-zA-Z0-9_]+\}\/)?([a-zA-Z0-9_\/]+)[\'\"]{1}[\s]*(#[.]*)?/ # regex to check for a require or require_relative line
  
  def probable_dependencies(filename)
    matchys, deps = [], []
    pn = Pathname.new filename
    
    # Get all possible dependencies in the current file
    open_file(filename) do |f|
      f.each do |l|
        begin
          if l =~ @@req_regex
            deps << l.scan(@@req_regex)[0][2]
          # else
          #   puts l if l.include? "require"
          end
        rescue ArgumentError
          puts "Failed to parse line %s" % l
        end
      end
    end
    
    # puts "deps"
    # p deps
    # puts "---"
    
    # Search filelist for matches for all dependencies
    deps.each do |dep|
      dep = dep + ".rb"
      depmatch = []
      attempted_resolve = (pn.dirname + dep).cleanpath
      if @filelist.has_key?(dep) # If it exists directly
        depmatch << dep
      elsif @filelist.has_key?(attempted_resolve) # If we can resolve the path
        depmatch << attempted_resolve
      else
        @filelist.each do |k,v|
          depmatch << k if k.include? dep
        end
      end
      matchys << depmatch
    end
    matchys
  end
end

# rbm = RubyFilesMatcher.new '../rails'
# rbm.dependency_graph_to_file('rails_dep.txt')