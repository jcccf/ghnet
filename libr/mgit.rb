# encoding=utf-8
require 'grit'
require 'json'
require 'pathname'
require 'iconv'
require_relative 'mnode'
require_relative 'massociation'
require_relative 'mfile'

class MGit
  
  def initialize(directory)
    @directory = directory
    @repo = Grit::Repo.new(@directory)
  end
  
  # Return num_commits from the end, and paginate if necessary
  def commits_all(num_commits)
    # Check for 'master' branch and switch to that if it exists
    # main_branch = nil
    # @repo.heads().each do |head|
    #   main_branch = "master" if head.name == "master"
    # end
    main_branch = @repo.head().name
    # Get commits on that branch
    if num_commits > 50
      i = num_commits / 25
      (0..i).each do |i|
        yield @repo.commits(main_branch, 25, i*25)
      end
    else
      yield @repo.commits(main_branch, num_commits)
    end
  end
  
  # Return a list of modified files for each commit
  def files_commits(num_commits)
    @repo = Grit::Repo.new(@directory)
    related_files = []
    commits_all(num_commits) do |commits|
      commits.each do |commit|
        paths = []
        begin
          commit.diffs.each do |diff|
            if diff.a_path != diff.b_path
              related_files += [[diff.a_path, diff.b_path]]
            end
            paths += [diff.a_path, diff.b_path]
          end
        rescue Grit::Git::GitTimeout
          puts "Failed to diff for %s" % commit.sha
        end
        paths.uniq!
        yield commit, paths
      end
    end
  end
  
  # Generate graph where cliques are frequent files commonly modified together (itemsets)
  # Edge weight is the frequency of that itemset
  def file_commits_itemsets(num_commits, filename, json_filename)
    pathlists = []
    files_commits(num_commits) do |commit, paths|
      pathlists << paths
    end
    
    itemsets = nil
    chdir_return('../../..') do
      itemsets = frequent_itemsets(pathlists, 3, 2)
      # puts itemsets
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
  
  # Generate graph where nodes are files, edges are commits
  def files_commits_graph(num_commits, filename)
    @repo = Grit::Repo.new(@directory)
    related_files = []
    
    g = MGraph.new
    files_commits(num_commits) do |commit, paths|
      paths.combination(2).each do |i, j|
        g.edge_inc(i, j)
      end
    end
    g.to_file(filename)
  end
  
  # Generate graph where nodes are authors, edges are files (modified in commits by the author)
  # Weights are # of common files between authors
  def authors_files_graph(num_commits, filename)
    @repo = Grit::Repo.new(@directory)
    related_files = []
    pathlist = {}

    files_commits(num_commits) do |commit, paths|
      auth = parse_name(commit.author_string)
      paths.each do |path|
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
  
end

def parse_name(author_string)
  author_string.force_encoding('utf-8').match(/([\p{Word}\(\)\. \'\?]+) <([a-zA-Z0-9_@\.\+\-\(\) ]+)>\w*/)[1]
  # p "föö. fo <abc@def.ghi> asd.a".match(/([\p{Word}\. ]+) <([a-zA-Z0-9_@\.\+]+)>\w*/)[0] == "föö. fo <abc@def.ghi>"
rescue
  p author_string
  "UNPARSEABLE_AUTHOR"
end

def repo_all_commits(repo_dir, filename)
  
  base_dir = Pathname.new(repo_dir).basename.to_s
  commits = []
  
  make_temp_dir do |tmpdir|
    # Copy repo to temp folder
    FileUtils.cp_r repo_dir, tmpdir
    temp_repo_dir = tmpdir + "/" + base_dir
    
    # Keep reading commits until we can't rewind anymore
    mg = MGit.new(temp_repo_dir)    
    keep_going = true
    while keep_going do
      # Read 1 commit
      i = 0
      mg.files_commits(1) do |commit, paths|
        commits << {"sha" => commit.sha, "author" => commit.author_string.to_json_raw_object, "paths" => paths.map {|p| p.to_json_raw_object}}
        i += 1
      end
      raise 'Too Many Commits Error: %d' % i if i > 1
    
      # Rewind 1 commit
      chdir_return(temp_repo_dir) do
        puts "Rewinding..."
        stdin, stdout, stderr = Open3.popen3("git reset --hard HEAD~1")
        keep_going = false if stderr.readlines.length > 0 # While not getting "...unknown revision or path not in the working tree..."
      end
    end
  end

  # Output to JSON {sha, author, paths}  
  File.open(filename, 'wb') do |f|
    f.write(JSON.generate(commits))
  end
end

if __FILE__ == $0
  repo_all_commits('../temp/compass', 'compasscommits.txt')
  # mg = MGit.new '../rails'
  # mg.authors_files_graph(50, "auth.txt")
  # mg.commits_all(1000) do |commits|
  #     puts commits[0]
  #   end
end