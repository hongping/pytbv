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

def __getattr__(name):
    return getattr(Kernel.inst(), name)