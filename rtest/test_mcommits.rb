require_relative '../libr/mcommits.rb'
require 'test/unit'

class TestMCommits < Test::Unit::TestCase
  
  # Ensure no commits are repeated
  # Ensure that all commits are seen
  def test_each
    mc = MCommits.new('data/all_commits/cloud-crowd.txt', 199, true)  
    a = Set.new
    size = 0
    previous_commits = nil
    i = 0
    mc.each do |commits|
      size += commits.size
      commits.each do |commit|
        a << commit['sha']
      end
      cset = Set.new(commits)
      unless previous_commits.nil?
        if cset.size == 199
          assert_equal 398, (cset ^ previous_commits).size
        else
          assert_equal cset.size + 199, (cset ^ previous_commits).size
        end
      end
      previous_commits = cset
      i += 1
    end
    assert_equal a.size, size
    assert_equal size, mc.all_commits.size
    assert_equal i, mc.num_blocks
  end
  
  # Ensure unique elements between each yield is 2 * increment
  # Ensure that all commits are seen
  def test_each_sliding_window
    mc = MCommits.new('data/all_commits/cloud-crowd.txt', 200, true) 
    a = Set.new
    size = 0
    previous_commits = nil
    mc.each_sliding_window(13) do |commits|
      size += commits.size
      commits.each do |commit|
        a << commit['sha']
      end
      cset = Set.new(commits)
      unless previous_commits.nil?
        if cset.size == 200
          assert_equal 26, (cset ^ previous_commits).size
        else
          assert_equal 13-(200-cset.size) + 13, (cset ^ previous_commits).size
        end
      end
      previous_commits = cset
    end
    assert_equal a.size, mc.all_commits.size
  end
  
  def test_each_date
    require 'time'
    mc = MCommits.new('data/all_commits/cloud-crowd.txt', 200, true)
    a = Set.new
    size = 0
    mc.each_date(86400) do |commits|
      size += commits.size
      commits.each do |commit|
        a << commit['sha']
      end
      assert Time.parse(commits[-1]['date']) - Time.parse(commits[0]['date']) < 86400
    end
    assert_equal a.size, size
    assert_equal size, mc.all_commits.size
  end

end