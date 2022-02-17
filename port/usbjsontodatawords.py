from __future__ import print_function
from __future__ import absolute_import
from builtins import object
import sys
import dill as pickle
import os
from collections import OrderedDict
from . import adt
import json

from .dataword import DataWord
from .dataword import UninterestingDataWord


class USBJSONToDatawords(object):
    def __init__(self, containerbuilder, usbjson_path):
        self.containerbuilder = containerbuilder
        self.usbjson_path = usbjson_path

    def get_datawords(self):
        with open(self.usbjson_path, "r") as f:
            j = json.loads(f.read())
        datawords = []
        for i in j:
            datawords.append(self.handle_event(i))
        return datawords

    def get_mutated_event(self, dw):
        # out = {}
        # out["jsonrpc"] = "2.0"
        # out["method"] = dw.container["type"]
        # out["id"] = dw.original_event["id"]
        # out["params"] = dw.original_event["params"]
        # if dw.captured_arguments:
        #     for i in dw.captured_arguments:
        #         out["params"][int(i["arg_pos"])] = i["members"][0]

        # return json.dumps(out)
        raise NotImplementedError

    def handle_event(self, event):
        proto = event['_source']['layers']['frame']['frame.protocols']
        if proto.startswith("usb:"):
          proto = proto.split(":", 1)[1]

        ## At this point method should be 'usb' or 'usbhid'

          argslist = [
          event['_source']['layers']['usb']["usb.src"],
          event['_source']['layers']['usb']["usb.dst"],
          event['_source']['layers']['usb']["usb.usbpcap_header_len"],
          event['_source']['layers']['usb']["usb.irp_id"],
          event['_source']['layers']['usb']["usb.usbd_status"],
          event['_source']['layers']['usb']["usb.function"],
          event['_source']['layers']['usb']["usb.irp_info"],
          event['_source']['layers']['usb']["usb.bus_id"],
          event['_source']['layers']['usb']["usb.device_address"],
          event['_source']['layers']['usb']["usb.endpoint_address"],
          event['_source']['layers']['usb']["usb.transfer_type"],
          event['_source']['layers']['usb']["usb.data_len"],
          event['_source']['layers']['usb']["usb.bInterfaceClass"],
          event['_source']['layers']["usbhid.data"]
          ]

        if not any(
            self.containerbuilder.top_level.values()
        ) or not self.containerbuilder.top_level.get(proto):
            return UninterestingDataWord(event)
        else:
            # JSON flavored operation here to get the return value from result
            # message
            # argslist.append(event.ret[0])
            container = self.containerbuilder.instantiate_type(proto)
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
        funcs = {"String": str, "Numeric": int}
        # will have to deal with return values from result messages
        # if arg_pos == "ret":
        #  return funcs[out_type](argslist[-1])
        # else:
        return funcs[out_type](argslist[int(arg_pos)])
