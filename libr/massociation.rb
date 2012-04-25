# MAssociation - association rule and frequent itemset algorithms

require_relative 'mfile'
require 'open3'

# Returns frequent itemsets
# Requires Christian Borgelt's FPgrowth in /bin (http://www.borgelt.net/fpgrowth.html)
def frequent_itemsets(stringlists, min_support="10%", min_itemset_size=2)
  min_support = (min_support.to_s.include? "%") ? min_support.to_s.gsub("%", "") : "-"+min_support.to_s # Format properly for FPgrowth
  itemsets = []
  make_temp_dir do |tmpdir| # Create a temporary working directory
    # Generate input file
    File.open(tmpdir+'/in.txt', 'w') do |f|
      stringlists.each do |stringlist|
        f.puts stringlist.map {|s| s.gsub(' ', '<SP>')}.join(" ")
      end
    end
    
    # Call fpgrowth
    stdin, stdout, stderr = Open3.popen3("bin/fpgrowth %s %s -tc -Z -s%s -m%d" % [tmpdir+'/in.txt', tmpdir+'/out.txt', min_support, min_itemset_size])
    if stdout.readlines.size > 0    
      # Read output file
      File.open(tmpdir+'/out.txt', 'r').each do |l|
        parts = l.split(' ')
        itemset = parts[0..-2].map {|s| s.gsub('<SP>', ' ')}
        frequency = parts[-1].gsub(/\((\w+)\)/, '\1').to_i
        itemsets << [itemset, frequency]
      end
    else
      puts "No Frequent Itemsets Found!"
    end
  end
  
  itemsets
end

if __FILE__ == $0
  p frequent_itemsets([["hello", "world", "how am i?"], ["i", "should", "know that"], ["i", "should", "gothere"]], 2, 2)
end