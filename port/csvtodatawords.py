from __future__ import print_function
from __future__ import absolute_import
from builtins import object
import sys
import dill as pickle
import os
from collections import OrderedDict
from . import adt
import csv

from .dataword import DataWord
from .dataword import UninterestingDataWord


class CSVToDatawords(object):
    def __init__(self, containerbuilder, csv_path):
        self.containerbuilder = containerbuilder
        self.csv_path = csv_path

    def get_datawords(self):
        with open(self.csv_path, "r") as file:
            reader = csv.reader(file)
            datawords = []
            for row in reader:
                datawords.append(self.handle_event(row))
        return datawords

    def get_mutated_event(self, dw):  # output this to a csv file with csv reader
        out = []
        # copy down the original event
        for i in dw.original_event:
            out.append(i)
        if dw.captured_arguments:
            for j in dw.captured_arguments:
                out[7 + int(j["arg_pos"])] = j["members"][0]
        output = out[0]
        for k in range(1, len(out)):
            output += "," + out[k]
        return output

    def handle_event(self, event):
        if not any(
            self.containerbuilder.top_level.values()
        ) or not self.containerbuilder.top_level.get(event[6]):
            return UninterestingDataWord(event)
        else:
            length = len(event)
            argslist = []

            # event args starts at index 7 after event name at index 6
            # if there is a return value, it will be at the end of the line included in argslist
            for i in range(7, length):
                argslist.append(event[i])
            container = self.containerbuilder.instantiate_type(event[6])
            container = self._capture_args(container, argslist)
            return DataWord(event, container)

    def _capture_args(self, container, argslist):
        for i in container["members"]:
            if i["type"] in self.containerbuilder.primatives:
                i["members"].append(
                    self._get_arg_as_type(i["arg_pos"], i["type"], argslist)
                )
            else:
                self._capture_args(i, argslist[int(i["arg_pos"])])
        return container

    def _get_arg_as_type(self, arg_pos, out_type, argslist):

        # not sure if this part need to be changed
        funcs = {"String": str, "Numeric": int}
        # will have to deal with return values from result messages
        # if arg_pos == "ret":
        #  return funcs[out_type](argslist[-1])
        # else:
        return funcs[out_type](argslist[int(arg_pos)])
