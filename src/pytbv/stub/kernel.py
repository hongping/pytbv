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


class CbClosure(object):
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

    def __init__(self):
        self.version = "0.0.1"
        self.product = "python stub"
        
        self.root = SimObject(self, "top")

        self.simulation_time = 0
        self.precision = -9
        self.callbacks = []
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
        ret = CbClosure(t, cb, ud)
        if len(self.callbacks) == 0:
            self.callbacks.append(ret)
            return ret

        cumulative_time = 0
        for i, existing_cb in enumerate(self.callbacks):
            cumulative_time += existing_cb.time_off
            
            if ret.time_off < cumulative_time:
                ret.time_off = ret.time_off - (cumulative_time - existing_cb.time_off)
                existing_cb.time_off -= ret.time_off
                self.callbacks.insert(i, ret)
                return ret

        ret.time_off -= cumulative_time
        self.callbacks.append(ret)
        return ret

    def run(self):
        while not self._stop_request and (len(self.callbacks) > 0):
            callback = self.callbacks.pop(0)
            self.simulation_time += callback.time_off
            callback()
 
        return self._stop_request
    
    @classmethod
    def inst(cls):
        if cls._inst is None:
            cls._inst = Kernel()
        return cls._inst

    @classmethod
    def init(cls):
        cls._inst = Kernel()
        return cls._inst
