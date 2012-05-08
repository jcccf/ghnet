#!/usr/bin/env ruby
# encoding: UTF-8
require 'fileutils'
require 'pathname'
require 'open3'
require_relative 'mgit'
require_relative 'mfilesmatcher'
require_relative 'mfile'
require_relative 'mcommits'
require_relative 'mdirectorystructure'
require_relative 'mcollections'
require 'optparse'

def generate_features(commits, base_dir, output_dir, i, commit_index, file_kenc, auth_kenc)
  # Pick and Decode Directory Structure Graph
  puts "Generating Dir Structure Graph"
  FileUtils.cp "data/all_structures/%s/dir/%d.txt" % [base_dir, commit_index], "%s/dir_%d.txt" % [output_dir, i]
        
  # Pick and Decode Dependency Graph
  puts "Generating Dependency Graph"
  FileUtils.cp "data/all_structures/%s/dep/%d.txt" % [base_dir, commit_index], "%s/dep_%d.txt" % [output_dir, i]

  # Generate Commit Graph from last N commits
  puts "Generating Commits Graph"
  files_commits_graph(commits, "%s/fc_%d.txt" % [output_dir, i], file_kenc)
          
  # Generate Frequent Itemsets
  puts "Generating Frequent Itemsets"
  file_commits_itemsets(commits, "%s/fq_%d.txt" % [output_dir, i], "%s/json_fq_%d.txt" % [output_dir, i], file_kenc)
          
  # Generate Author Graphs
  puts "Generating Author Graphs"
  authors_files_graph(commits, "%s/au_%d.txt" % [output_dir, i], auth_kenc)
    
  # Generate Author Frequencies
  puts "Generating Author Frequencies"
  author_frequencies(commits, "%s/af_%d.txt" % [output_dir, i], auth_kenc)
end

def dependency_history(source_dir, num_commits, sliding_window=False, sliding_window_increment=10)
  base_dir = Pathname.new(source_dir).basename.to_s
  n = (sliding_window) ? "%d_%d" % [num_commits, sliding_window_increment] : num_commits.to_s
  output_dir = "data/dependency_graphs/%s/%s" % [base_dir, n]
  puts output_dir
  FileUtils.mkdir_p output_dir
  mc = MCommits.new('data/all_commits/%s.txt' % base_dir, num_commits, true)
  # mc.add_parsed_authors
  file_kenc, auth_kenc = KeyEncoder.new('data/all_structures/%s/file_key.txt' % base_dir), KeyEncoder.new('data/all_structures/%s/auth_key.txt' % base_dir)
  if sliding_window
    i, commit_index = 0, num_commits-sliding_window_increment-1
    mc.each_sliding_window(sliding_window_increment) do |commits|
      commit_index += commits.size - (num_commits-sliding_window_increment)
      generate_features(commits, base_dir, output_dir, i, commit_index, file_kenc, auth_kenc)
      i += 1
    end
  else
    i, commit_index = 0, -1
    mc.each do |commits|
      commit_index += commits.size
      generate_features(commits, base_dir, output_dir, i, commit_index, file_kenc, auth_kenc)
      i += 1
    end
  end
end

def over_all_time(source_dir)
  base_dir = Pathname.new(source_dir).basename.to_s
  mc = MCommits.new('data/all_commits/%s_detailed.txt' % base_dir)
  output_dir = "data/all_time/%s" % base_dir
  FileUtils.mkdir_p output_dir
  commits = mc.all_commits
  
  authors_additions_deletions(commits, "%s/author_add_del.txt" % output_dir)
  file_commits_itemsets(commits, "%s/itemsets_graph.txt" % output_dir, "%s/itemsets_json.txt" % output_dir)
  file_commits_graph(commits, "%s/commits_graph.txt" % output_dir)
end

if __FILE__ == $0
  action = nil
  sliding_window = false
  OptionParser.new do |opts|
    opts.banner = "Usage: main.rb [options]"
    opts.on("-g", "--generate", "Commit Logs and Structure History") { |v| action = :generate }
    opts.on("-f", "--features", "Commit Features") { |v| action = :features }
    opts.on("-a", "--all", "Over all") { |v| action = :all }
    opts.on("-w", "--window", "Add Sliding Window for Features") { |v| sliding_window = true }
  end.parse!
  
  case action
  when :generate # Step 1
    puts "Generating commit logs and structure history"
    Dir.entries('../temp').find_all { |f| File.directory?('../temp/'+f) && f != '.' && f != '..' }.each do |dir|
      puts dir
      repo_all_commits("../temp/%s" % dir, 'data/all_commits/%s.txt' % dir, 'data/all_commits/%s_detailed.txt' % dir) unless File.exist? 'data/all_commits/%s.txt' % dir
      repo_all_commits_structures('../temp/%s' % dir, 'data/all_commits/%s.txt' % dir, 'data/all_structures/%s' % dir) unless File.exist? 'data/all_structures/%s/file_key.txt' % dir
      repo_all_commits_authors('../temp/%s' % dir, 'data/all_commits/%s.txt' % dir, 'data/all_structures/%s' % dir) unless File.exist? 'data/all_structures/%s/auth_key.txt' % dir
    end
  when :features # Step 2
    puts "Generating file features"
    puts "...with sliding window" if sliding_window
    Dir.entries('../temp').find_all { |f| File.directory?('../temp/'+f) && f != '.' && f != '..' }.each do |dir|
      puts dir
      dir_num = sliding_window ? "200_10" : "200"
      dependency_history("../temp/%s" % dir, 200, sliding_window) # unless File.exist? 'data/dependency_graphs/%s/%s/af_0.txt' % [dir, dir_num]
      # all_itemset_occurrences("data/all_commits/%s_detailed.txt" % dir, "data/dependency_graphs/%s/%s" % [dir, dir_num], 0.1, KeyEncoder.new('data/all_structures/%s/file_key.txt' % dir)) unless File.exist? 'data/dependency_graphs/%s/%s/itemset_occurrences/0.txt' % [dir, dir_num]
    end
  when :all
    Dir.entries('../temp').find_all { |f| File.directory?('../temp/'+f) && f != '.' && f != '..' }.each do |dir|
      over_all_time(dir)
    end
  end
end