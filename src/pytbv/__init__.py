"""
mock hardware simulator initialize and running simulation
"""

import os
import sys
import importlib
from packaging import version

# monkey patch cocotb simulator module
sys.modules["cocotb.simulator"] = importlib.import_module("pytbv.stub.simulator")

import cocotb_tools._coverage
import cocotb
import cocotb._init

"""
during cocotb initialization, there is direct calling of cocotb.simulator,
hence needed a direct assignment of cocotb.simulator to the Python interface 
"""
cocotb.simulator = sys.modules["cocotb.simulator"]

if version.parse(cocotb.__version__) < version.parse("2.0.0"):
    print("ERROR: pytbv requires cocotb version >= 2.0.0")
    sys.exit(1)

from .stub.kernel import Kernel

def run(cocotb_test_module):
    os.environ["COCOTB_TEST_MODULES"] = cocotb_test_module

    kernal = Kernel.init()

    """
    called in pygpi entry to start cocotb
    """
    cocotb_tools._coverage.start_cocotb_library_coverage([])
    cocotb.logging._configure([])
    cocotb._init.init_package_from_simulation([])
    cocotb._init.run_regression([])

    
    kernal.run()
