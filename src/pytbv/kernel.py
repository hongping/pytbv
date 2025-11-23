# Copyright (c) 2025 Tan, Hong Ping
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .gpi_constants import *
import importlib

class SimObject(object):
    def __init__(self, kernel, name):
        self.kernel = kernel
        self.name = name


class gpi_sim_hdl(object):
    def __init__(self, simobject):
        self.simobject = simobject
    
    def get_type(self):
        return MODULE
    
    def get_type_string(self):
        return "module"

    def get_name_string(self):
        return self.simobject.name
    
    def get_definition_name(self):
        return self.simobject.__class__.__name__
    
    def get_definition_file(self):
        module = importlib.import_module(self.simobject.__class__.__module__)
        return module.__file__


class CbTimed(object):
    def __init__(self, time_off, cb, ud):
        self.time_off = time_off
        self.cb = cb
        self.ud = ud

    def __call__(self):
        if self.cb is not None:
            self.cb(self.ud)

    def deregister(self):
        self.cb = None


class Kernel(object):
    _inst = None

    def __init__(self, **kwargs):
        self.version = "0.0.1"
        self.product = "python stub"
        
        self.root = SimObject(self, "top")

        self.simulation_time = 0
        self.precision = -9
        self.scheduled_callbacks = []
        self._stop_request = False

    def get_simulator_product(self):
        return self.product

    def get_simulator_version(self):
        return self.version

    def get_root_handle(self):
        return gpi_sim_hdl(self.root)

    def get_sim_time(self):
        time = self.simulation_time
        return ((time >> 32), time & 0xFFFFFFFF)

    def stop_simulator(self):
        self._stop_request = True

    def register_timed_callback(self, t, cb, ud):
        ret = CbTimed(t, cb, ud)
        
        # Schedule at absolute time
        absolute_time = self.simulation_time + t
        ret.time_off = absolute_time # Store absolute time temporarily for sorting

        if len(self.scheduled_callbacks) == 0:
            self.scheduled_callbacks.append(ret)
            return ret

        for i, existing_cb in enumerate(self.scheduled_callbacks):
            if ret.time_off < existing_cb.time_off:
                self.scheduled_callbacks.insert(i, ret)
                return ret

        self.scheduled_callbacks.append(ret)
        return ret

    def run(self):
        while not self._stop_request:
            if not self.scheduled_callbacks:
                break

            next_event_time = self.scheduled_callbacks[0].time_off
            self.simulation_time = next_event_time

            # Process Timer events at this time
            while self.scheduled_callbacks and self.scheduled_callbacks[0].time_off == self.simulation_time:
                callback = self.scheduled_callbacks.pop(0)
                callback()
 
        return self._stop_request
    
    @classmethod
    def inst(cls):
        if Kernel._inst is None:
            Kernel._inst = Kernel()
        return Kernel._inst

    @classmethod
    def init(cls, **kwargs):
        Kernel._inst = cls(**kwargs)
        return Kernel._inst
