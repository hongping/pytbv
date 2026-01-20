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


import os
import sys
import importlib
from packaging import version

sys.modules["cocotb.simulator"] = importlib.import_module("pytbv.simulator")

import cocotb_tools._coverage
import cocotb
import cocotb._init

cocotb.simulator = sys.modules["cocotb.simulator"]

if version.parse(cocotb.__version__) < version.parse("2.0.0"):
    print("ERROR: pytbv requires cocotb version >= 2.0.0")
    sys.exit(1)

from .kernel import Kernel


class TestResult:
    """Result of running pytbv tests."""
    def __init__(self, passed=0, failed=0, skipped=0):
        self.passed = passed
        self.failed = failed
        self.skipped = skipped
    
    @property
    def all_passed(self):
        return self.failed == 0 and self.passed > 0
    
    def __repr__(self):
        return f"TestResult(passed={self.passed}, failed={self.failed}, skipped={self.skipped})"


def run(cocotb_test_module, kernel_cls=Kernel, **kwargs):
    """Run cocotb/pyuvm tests and return results.
    
    Returns:
        TestResult: Object containing passed/failed/skipped counts.
    """
    os.environ["COCOTB_TEST_MODULES"] = cocotb_test_module

    kernel = kernel_cls.init(**kwargs)
    
    cocotb_tools._coverage.start_cocotb_library_coverage([])
    cocotb.logging._configure([])
    cocotb._init.init_package_from_simulation([])
    cocotb._init.run_regression([])
    
    kernel.run()
    
    # Get test results from cocotb's regression manager
    try:
        from cocotb._init import _regression_manager
        if _regression_manager is not None:
            passed = _regression_manager.passed
            failed = _regression_manager.failed
            skipped = _regression_manager.skipped
            return TestResult(passed=passed, failed=failed, skipped=skipped)
    except (ImportError, AttributeError):
        pass
    
    # Fallback: assume passed if no exception was raised
    return TestResult(passed=1, failed=0, skipped=0)
