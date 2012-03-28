# encoding=utf-8
require 'grit'
require_relative 'mnode'

def parse_name(author_string)
  author_string.force_encoding('utf-8').match(/([\p{Word}\. ]+) <([a-zA-Z0-9_@\.\+]+)>\w*/)[1]
  # p "föö. fo <abc@def.ghi> asd.a".match(/([\p{Word}\. ]+) <([a-zA-Z0-9_@\.\+]+)>\w*/)[0] == "föö. fo <abc@def.ghi>"
end

repo = Grit::Repo.new("../rails")

commits = repo.commits('master', 50) # 10, 20 for paging, returns 21-30

related_files = []

files = NodeDict.new

commits.each do |commit|
  paths = []
  commit.diffs.each do |diff|
    if diff.a_path != diff.b_path
      related_files += [[diff.a_path, diff.b_path]]
    end
    paths += [diff.a_path, diff.b_path]
    paths.uniq!
  end
  paths.each { |path| files[path] ||= Node.new(path) }
  paths.each do |path|
    paths.each do |path2|
      files[path].edge(path2) if path != path2
    end
  end  
  # puts parse_name(commit.author_string)
  # puts paths
end

puts files
files.to_file('list.txt')