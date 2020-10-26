class DataWord(object):
  def __init__(self, event, container):
    self.original_event = event
    self.container = container
    self.predicate_results = []
    if container:
      self.type = container["type"]
      self.captured_arguments = container["members"]
    else:
      # HACK HACK HACK:  we have to find out if we have a system call or a
      # jsonrpc call as our event
      if hasattr(self.original_event, "name"):
        self.type = self.original_event.name
      else:
        self.type = self.original_event["procedure"]
      self.captured_arguments = None


  def is_interesting(self):
    return True


  def get_name(self):
    return self.type


  def get_dataword(self):
    tmp = ''
    tmp += self.type
    tmp += '('
    # Only print dataword parameters if we have them
    if self.container:
      tmp += ', '.join([str(x["members"][0]) for x in self.captured_arguments])
    tmp += ')'
    return tmp





class UninterestingDataWord(DataWord):
  def __init__(self, event):
    super(UninterestingDataWord, self).__init__(event, {})

  def is_interesting(self):
    return False
