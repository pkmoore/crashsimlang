from __future__ import print_function
from __future__ import absolute_import
from builtins import object
import sys
import dill as pickle
import os
from collections import OrderedDict
from . import adt
import json
import copy

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
        # For uninteresting datawords, we return the original event,
        # unmodified event
        if not dw.is_interesting():
            return dw.original_event
        out = copy.deepcopy(dw.original_event)
        maybe_data = self._get_arg_by_name("src", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.src"] = maybe_data
        maybe_data = self._get_arg_by_name("dst", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.dst"] = maybe_data
        maybe_data = self._get_arg_by_name("usbpcap_header_len", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.usbpcap_header_len"] = maybe_data
        maybe_data = self._get_arg_by_name("irp_id", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.irp_id"] = maybe_data
        maybe_data = self._get_arg_by_name("usbd_status", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.usbd_status"] = maybe_data
        maybe_data = self._get_arg_by_name("function", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.function"] = maybe_data
        maybe_data = self._get_arg_by_name("irp_info", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.irp_info"] = maybe_data
        maybe_data = self._get_arg_by_name("bus_id", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.bus_id"] = maybe_data
        maybe_data = self._get_arg_by_name("device_address", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.device_address"] = maybe_data
        maybe_data = self._get_arg_by_name("endpoint_address", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.endpoint_address"] = maybe_data
        maybe_data = self._get_arg_by_name("transfer_type", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.transfer_type"] = maybe_data
        maybe_data = self._get_arg_by_name("data_len", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.data_len"] = maybe_data
        maybe_data = self._get_arg_by_name("bInterfaceClass", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usb"]["usb.bInterfaceClass"] = maybe_data
        maybe_data = self._get_arg_by_name("data", dw.captured_arguments)
        if maybe_data:
            out["_source"]["layers"]["usbhid.data"] = maybe_data
        return json.dumps(out)

    def handle_event(self, event):
        proto = event["_source"]["layers"]["frame"]["frame.protocols"]
        if proto.startswith("usb:"):
            proto = proto.split(":", 1)[1]

            ## At this point method should be 'usb' or 'usbhid'

            argslist = [
                event["_source"]["layers"]["usb"]["usb.src"],
                event["_source"]["layers"]["usb"]["usb.dst"],
                event["_source"]["layers"]["usb"]["usb.usbpcap_header_len"],
                event["_source"]["layers"]["usb"]["usb.irp_id"],
                event["_source"]["layers"]["usb"]["usb.usbd_status"],
                event["_source"]["layers"]["usb"]["usb.function"],
                event["_source"]["layers"]["usb"]["usb.irp_info"],
                event["_source"]["layers"]["usb"]["usb.bus_id"],
                event["_source"]["layers"]["usb"]["usb.device_address"],
                event["_source"]["layers"]["usb"]["usb.endpoint_address"],
                event["_source"]["layers"]["usb"]["usb.transfer_type"],
                event["_source"]["layers"]["usb"]["usb.data_len"],
                event["_source"]["layers"]["usb"]["usb.bInterfaceClass"],
                event["_source"]["layers"]["usbhid.data"],
            ]

        if not any(
            self.containerbuilder.top_level.values()
        ) or not self.containerbuilder.top_level.get(proto):
            return UninterestingDataWord(event)
        else:
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

    def _get_arg_by_name(self, name, members):
        candidates = tuple(x for x in members if x["arg_name"] == name)
        assert len(candidates) <= 1, f"Multiple arguments for name {name}: {candidates}"
        if len(candidates) == 0:
            return None
        value = candidates[0]["members"]
        assert len(value) == 1, f"Multiple values for name {name}"
        return candidates[0]["members"][0]
