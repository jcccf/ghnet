require 'fileutils'
require 'pathname'
require 'open3'
require_relative 'mgit'
require_relative 'mfilesmatcher'
require_relative 'mfile'
require_relative 'mcommits'
require_relative 'mdirectorystructure'
require_relative 'mcollections'

def dependency_history(source_dir, num_commits)
  base_dir = Pathname.new(source_dir).basename.to_s
  base_output_dir = "data/dependency_graphs/%s/%d" % [base_dir, num_commits]
  FileUtils.mkdir_p base_output_dir
  rel_output_dir = base_output_dir
  mc = MCommits.new('data/commits_all/%s.txt' % base_dir, num_commits, true)
  i, commit_index = 0, -1
  dir_kenc, dep_kenc = KeyEncoder.new('data/all_structures/%s/dir_key.txt' % base_dir), KeyEncoder.new('data/all_structures/%s/dep_key.txt' % base_dir)
  mc.each do |commits|
    commit_index += commits.size
    # Pick and Decode Directory Structure Graph
    puts "Generating Dir Structure Graph"
    decode_mgraph_csv("data/all_structures/%s/dir/%d.txt" % [base_dir, commit_index], "%s/dir_%d.txt" % [rel_output_dir, i], dir_kenc)
        
    # Pick and Decode Dependency Graph
    puts "Generating Dependency Graph"
    decode_mgraph_csv("data/all_structures/%s/dep/%d.txt" % [base_dir, commit_index], "%s/dep_%d.txt" % [rel_output_dir, i], dep_kenc)

    # Generate Commit Graph from last N commits
    puts "Generating Commits Graph"
    files_commits_graph(commits, "%s/fc_%d.txt" % [rel_output_dir, i])
          
    # Generate Frequent Itemsets
    puts "Generating Frequent Itemsets"
    file_commits_itemsets(commits, "%s/fq_%d.txt" % [rel_output_dir, i], "%s/json_fq_%d.txt" % [rel_output_dir, i])
          
    # Generate Author Graphs
    puts "Generating Author Graphs"
    authors_files_graph(commits, "%s/au_%d.txt" % [rel_output_dir, i])
    i += 1
  end
end

# puts "Generating Commit Logs and Structure History"
# Dir.entries('../temp').find_all { |f| File.directory?('../temp/'+f) && f != '.' && f != '..' }.each do |dir|
#   puts dir
#   repo_all_commits("../temp/%s" % dir, 'data/all_commits/%s.txt' % dir, 'data/all_commits/%s_detailed.txt' % dir)
#   repo_all_commits_structures('../temp/%s' % dir, 'data/all_commits/%s.txt' % dir, 'data/all_structures/%s' % dir)
# end

puts "Generating File Features"
Dir.entries('../temp').find_all { |f| File.directory?('../temp/'+f) && f != '.' && f != '..' }.each do |dir|
  puts dir
  dependency_history("../temp/%s" % dir, 200) if dir == 'cloud-crowd'
  # all_itemset_occurrences("data/all_commits/%s_detailed.txt" % dir, "data/dependency_graphs/%s/200" % dir)
end