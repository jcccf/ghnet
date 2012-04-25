# MFile - Useful helper functions
require 'fileutils'
require 'securerandom'
require 'json'

# Make a temporary directory in /temp, and delete its contents after you're done
def make_temp_dir
  # FileUtils.mkdir 'temp' unless File.exist? 'temp'
  rand_dir = 'temp/' + SecureRandom.hex(16)  
  FileUtils.mkdir_p rand_dir
  yield rand_dir
  FileUtils.rm_r rand_dir
end

# Change to this directory, and return after the block
def chdir_return(new_dir)
  curr_dir = Dir.pwd
  Dir.chdir new_dir
  yield
  Dir.chdir curr_dir
end

def json_to_file(object, filename)
  File.open(filename, 'w') do |f|
    f.write(JSON.generate(object))
  end
end

def json_from_file(filename)
  d = nil
  File.open(filename, 'r') do |f|
    d = f.read
  end
  JSON.parse(d)
end

if __FILE__ == $0
  make_temp_dir do |tempdir|
    puts tempdir
  end
end