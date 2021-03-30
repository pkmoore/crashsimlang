class DataWord(object):
  def __init__(self, event, container):
    self.original_event = event
    self.container = container
    self.predicate_results = []
    if container:
      self.type = container["type"]
      self.captured_arguments = container["members"]
    else:
      # HACK HACK HACK
      # Strace objects have a name field
      if hasattr(self.original_event, "name"):
        self.type = self.original_event.name
      # JSON objects have a "procedure" key
      elif "procedure" in self.original_event.keys():
        self.type = self.original_event["procedure"]
      # XMLRPC object have a methodName
      elif self.original_event[0].tag == "methodName":
        self.type = self.original_event[0].text
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
