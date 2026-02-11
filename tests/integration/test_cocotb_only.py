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

from pytbv import run

import pytest
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_simple(dut):
    dut._log.info("start")
    await Timer(10, unit="ns")
    dut._log.info("end")


# Pytest wrapper to run via pytest
@pytest.mark.integration
def test_cocotb_only_via_pytest():
    """Run cocotb test via pytest."""
    from pytbv.kernel import Kernel
    Kernel._inst = None  # Reset singleton
    result = run("tests.integration.test_cocotb_only")
    assert result.all_passed, f"cocotb test failed: {result}"


if __name__ == "__main__":
    run("tests.integration.test_cocotb_only")
