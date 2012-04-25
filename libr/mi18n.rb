class String
  def to_utf8
    begin
      self.force_encoding('utf-8')
    rescue
      Iconv.conv('utf-8', 'isso8859-1', self)
    end
  end
end