require 'rubygems'
require 'git'
require 'logger'
require 'grit'
g = Git.open('../../rails', :log => Logger.new(STDOUT))
# shas = []
# g.log(9999).each do |l|
#   shas << l.sha
# end
# shas.reverse!
# puts shas
# (0..(shas.size-2)).each do |i|
#   puts "###"
#   g.diff(shas[i],shas[i+1]).path('actionpack/lib/action_dispatch/http/mime_type.rb').each do |file_diff|
#     puts file_diff.patch
#     puts file_diff.type
#     puts g.gcommit(shas[i+1]).committer.name
#     puts g.gcommit(shas[i+1]).date.strftime("%m-%d-%y %H:%M:%S")
#   end
# end

# g.log(99).object('actionpack/lib/action_dispatch/http/mime_type.rb').each do |commit|
#   puts commit
# end

repo = Grit::Repo.new('../../rails')
# commits = repo.log('master', 'actionpack/lib/action_dispatch/http/mime_type.rb', {:follow => true, :n => 9999})
# commits.reverse!
# puts commits.size
# commits.each do |commit|
#   puts commit.sha
# end

# commits = repo.log('319ae4628f4e0058de3e40e4ca7791b17e45e70c', nil, {'M' => true, 'diff-filter' => 'R'})
# commits[0].diffs().each do |diff|
#   puts diff.a_path
# end


diffs = repo.diff('a0f2b1d95d3785de92ae271fd7ea23e91c0cadc6:actionpack/lib/action_controller/mime/type.rb', '319ae4628f4e0058de3e40e4ca7791b17e45e70c:actionpack/lib/action_dispatch/http/mime_type.rb')
puts diffs[0].inspect
# (0..(commits.size-2)).each do |i|
#   diffs = repo.diff(commits[i], commits[i+1], 'actionpack/lib/action_dispatch/http/mime_type.rb')
#   puts i, diffs.size
# end


# repo.diff('8c197fb4^',commits[-1]).each do |diff|
#   if diff.b_path == 'actionpack/lib/action_dispatch/http/mime_type.rb'
#     puts diff.inspect
#   end
# end

# df = repo.diff(commits[-1], commits[-2], 'actionpack/lib/action_dispatch/http/mime_type.rb')[0]
# puts commits[-1].sha
# puts df.renamed_file
# puts df.deleted_file
# puts df.new_file
# puts df.similarity_index
# puts df.diff
# bl = repo.blame('actionpack/lib/action_dispatch/http/mime_type.rb', commits[-1])
# puts bl.lines[3].line
# puts bl.lines[0].commit.author_string()
# puts bl.lines[0].commit.date()

# To go further back in time, use git blame, get commit shas, and see which is the most recent, then 