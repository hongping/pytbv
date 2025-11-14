"""
mock cocotb simulator interface implementation in Python.
"""

from .gpi_constants import *
from .kernel import gpi_sim_hdl
from .kernel import Kernel

def set_sim_event_callback(a):
    pass

def initialize_logger(a, b):
    pass

def get_simulator_product():
    return Kernel.inst().get_simulator_product()

def get_simulator_version():
    return Kernel.inst().get_simulator_version()

def get_sim_time():
    return Kernel.inst().get_sim_time()

def package_iterate():
    pass

def get_root_handle(a):
    return Kernel.inst().get_root_handle()

def get_precision():
    return Kernel.inst().precision

def stop_simulator():
    Kernel.inst().stop_simulator()

def register_timed_callback(t, cb, ud):
    return Kernel.inst().register_timed_callback(t, cb, ud)

def set_gpi_log_level(a):
    pass