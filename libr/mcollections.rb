# Class to map strings (mainly) to integers (and back again)
class KeyEncoder
  def initialize(filename=nil)
    if filename.nil?
      @hash = {}
      @counter = 0
    else
      File.open(filename, 'r') do |f|
        data = JSON.parse(f.read)
        @hash = data['hash']
        @counter = data['counter']
        @inv_hash = @hash.invert
      end
    end
  end
  
  def key_count
    @hash.size
  end
  
  def encode(string)
    if @hash.include? string
      @hash[string]
    else
      @counter += 1
      @hash[string] = @counter
    end
  end
  
  def decode(inty)
    @inv_hash[inty.to_i]
  end
  
  def to_file(filename)
    File.open(filename, 'w') do |f|
      f.write(JSON.generate({ :hash => @hash, :counter => @counter }))
    end
  end  
end
