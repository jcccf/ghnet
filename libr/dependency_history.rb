require 'fileutils'
require 'pathname'
require 'open3'
require_relative 'mgit'
require_relative 'mfilesmatcher'
require_relative 'mfile'
require_relative 'mcommits'

def dependency_history(source_dir, num_commits)
  base_dir = Pathname.new(source_dir).basename.to_s
  base_output_dir = "data/dependency_graphs/%s/%d" % [base_dir, num_commits]
  FileUtils.mkdir_p base_output_dir
  rel_output_dir = "../../../" + base_output_dir

  make_temp_dir do |tmpdir|
    FileUtils.cp_r source_dir, tmpdir
    temp_repo_dir = tmpdir + "/" + base_dir
    chdir_return(temp_repo_dir) do
      mg = MGit.new('.')
      mc = MCommits.new('../../../data/commits_all/%s.txt' % base_dir, num_commits, true)
      i = mc.num_blocks
      mc.reverse_each do |commits|
        i -= 1  
        # Generate Dependency Graph
        puts "Generating Dependency Graph"
        RubyFilesMatcher.new('.').dependency_graph_to_file("%s/dep_%d.txt" % [rel_output_dir, i])
         
        # Generate Commit Graph from last N commits
        puts "Generating Commits Graph"
        files_commits_graph(commits, "%s/fc_%d.txt" % [rel_output_dir, i])
      
        # Generate Frequent Itemsets
        puts "Generating Frequent Itemsets"
        file_commits_itemsets(commits, "%s/fq_%d.txt" % [rel_output_dir, i], "%s/json_fq_%d.txt" % [rel_output_dir, i])
      
        # Generate Author Graphs
        puts "Generating Author Graphs"
        authors_files_graph(commits, "%s/au_%d.txt" % [rel_output_dir, i])

        # Rewind N commits
        puts "Rewinding %d..." % commits.size
        stdin, stdout, stderr = Open3.popen3("git reset --hard HEAD~%d" % commits.size)
        puts "Rewound to End" if stderr.readlines.length > 0 # While not getting "...unknown revision or path not in the working tree..."
      end
    end
  end
end

# puts "Generating Commit Logs"
# Dir.entries('../temp').find_all { |f| File.directory?('../temp/'+f) && f != '.' && f != '..' }.each do |dir|
#   puts dir
#   repo_all_commits("../temp/%s" % dir, 'data/commits_all/%s.txt' % dir, 'data/commits_all/%s_detailed.txt' % dir)
# end

puts "Generating File Features"
Dir.entries('../temp').find_all { |f| File.directory?('../temp/'+f) && f != '.' && f != '..' }.each do |dir|
  puts dir
  # dependency_history("../temp/%s" % dir, 200)
  all_itemset_occurrences("data/commits_all/%s_detailed.txt" % dir, "data/dependency_graphs/%s/200" % dir)
end