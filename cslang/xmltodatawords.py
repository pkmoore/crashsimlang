from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object
import sys
import dill as pickle
import os
from collections import OrderedDict
from . import adt
from lxml import etree


from .dataword import DataWord
from .dataword import UninterestingDataWord

class XMLToDatawords(object):
  def __init__(self, containerbuilder, xml_path):
    self.containerbuilder = containerbuilder
    self.xml_path = xml_path


  def get_datawords(self):
    with open(self.xml_path, "r") as f:
      root = etree.fromstring(f.read())
    datawords = []
    for child in root:
      datawords.append(self.handle_event(child))
    return datawords

  def get_mutated_xml(self, dw):
    root = etree.Element("methodCall")
    mn = etree.Element("methodName")
    mn.text = dw.type
    root.append(mn)
    params = dw.original_event.find("params")
    if dw.captured_arguments:
      for i in dw.captured_arguments:
        params[int(i["arg_pos"])][0][0].text = str(i["members"][0])
    root.append(params)
    return etree.tostring(root)


  def handle_event(self, event):
    mn = event.find("methodName")
    method_name = mn.text
    params = event.find("params")
    p = []
    for param in params:
      xml_value = param[0][0].text
      p.append(xml_value)

    if not any(self.containerbuilder.top_level.values()) \
      or not self.containerbuilder.top_level.get(method_name):
      # Right now, we define a system call we aren't interested in as
      # any system call with no captured arguments
      return UninterestingDataWord(event)
    else:
      argslist = p
      # argslist.append(event.ret[0])
      container = self.containerbuilder.instantiate_type(method_name)
      container = self._capture_args(container, argslist)
      return DataWord(event, container)

  def _capture_args(self, container, argslist):
    for i in container["members"]:
      if i["type"] in self.containerbuilder.primatives:
        i["members"].append(self._get_arg_as_type(i["arg_pos"], i["type"], argslist))
      else:
        self._capture_args(i, argslist[int(i["arg_pos"])])
    return container

  def _get_arg_as_type(self, arg_pos, out_type, argslist):
    funcs = {"String": str,
             "Numeric": int
     }
    # will have to deal with return values from result messages
    #if arg_pos == "ret":
    #  return funcs[out_type](argslist[-1])
    #else:
    return funcs[out_type](argslist[int(arg_pos)])
