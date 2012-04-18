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
        yield commit, paths, related_files
      end
    end
  end
end

def parse_name(author_string)
  author_string.force_encoding('utf-8').match(/([\p{Word}\(\)\. \'\?]+) <([a-zA-Z0-9_@\.\+\-\(\) ]+)>\w*/)[1]
  # p "föö. fo <abc@def.ghi> asd.a".match(/([\p{Word}\. ]+) <([a-zA-Z0-9_@\.\+]+)>\w*/)[0] == "föö. fo <abc@def.ghi>"
rescue
  p author_string
  "UNPARSEABLE_AUTHOR"
end

def repo_all_commits(repo_dir, filename, detailed_filename)
  
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
      mg.files_commits(1) do |commit, paths, related|
        commit_arr = {:sha => commit.sha, :author => commit.author_string.to_json_raw_object, :message => commit.message.to_json_raw_object}
        commit_arr["paths"] = paths.map {|p| p.to_json_raw_object}
        commit_arr["related_files"] = related.map { |r1, r2| [r1.to_json_raw_object, r2.to_json_raw_object]}
        stat_files = {}
        commit.stats.files.each { |f,add,del,tot| stat_files[f.to_json_raw_object] = [add, del, tot] }
        commit_arr["stats"] = { :additions => commit.stats.additions, :deletions => commit.stats.deletions, :files => stat_files }
        commits << commit_arr
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
  commits.reverse! # Reverse order so that it is in ascending order of creation
  File.open(detailed_filename, 'wb') do |f|
    f.write(JSON.generate(commits))
  end
  commits.each { |c| c.delete("related_files"); c.delete("stats") }
  File.open(filename, 'wb') do |f|
    f.write(JSON.generate(commits))
  end
end

if __FILE__ == $0
  repo_all_commits('../temp/compass', 'compasscommits.txt', 'compasscommits_detailed.txt')
  # mg = MGit.new '../rails'
  # mg.authors_files_graph(50, "auth.txt")
  # mg.commits_all(1000) do |commits|
  #     puts commits[0]
  #   end
end