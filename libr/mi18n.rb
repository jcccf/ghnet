class String
  def to_utf8
    begin
      Iconv.conv('utf-8//ignore', 'utf-8', self.force_encoding('utf-8') + ' ')[0..-2]
    rescue
      Iconv.conv('utf-8//ignore', 'isso8859-1', self + ' ')[0..-2]
      # ic = Iconv.new('UTF-8//IGNORE', 'UTF-8')
      # ic.iconv(us + ' ')[0..-2]
    end
  end
end