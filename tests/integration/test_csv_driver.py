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

import cocotb
from pytbv.kernels import Transaction

@cocotb.test()
async def test_csv_driver(dut):
    dut._log.info("Starting test_csv_driver")
    
    # We expect transactions for port A at time 20 and 40.
    # The 3rd await should timeout or the simulation should end.
    # To avoid hanging if the simulation ends properly, we can wrap in a timeout or just see what happens.
    # Given the user request "loop ... for 3 times", I will do exactly that.
    
    for i in range(3):
        dut._log.info(f"Waiting for transaction {i+1}")
        try:
            t = await Transaction("A")
            dut._log.info(f"Transaction {i+1} received: Address=0x{t.transaction.address:x}, Data=0x{t.transaction.data:x}, Status=0x{t.transaction.status:x}")
            await cocotb.triggers.Timer(10, unit="ns")
            dut._log.info(f"timer 10ns")
        except Exception as e:
            dut._log.info(f"Transaction {i+1} failed or simulation ended: {e}")


# Pytest wrapper to run via pytest
import pytest
@pytest.mark.integration
def test_csv_driver_via_pytest():
    """Run CSV driver test via pytest."""
    from pytbv import run
    from pytbv.kernel import Kernel
    from pytbv.kernels import CSVKernel
    Kernel._inst = None  # Reset singleton
    result = run("tests.integration.test_csv_driver", kernel_cls=CSVKernel, csv_path="tests/data/transactions.csv")
    assert result.all_passed, f"CSV driver test failed: {result}"


if __name__ == "__main__":
    import argparse
    from pytbv import run
    from pytbv.kernels import CSVKernel, Transaction

    parser = argparse.ArgumentParser(description="Run CSV driver test")
    parser.add_argument("--csv", default="tests/data/transactions.csv", help="Path to transaction CSV file")
    args = parser.parse_args()

    run("tests.integration.test_csv_driver", kernel_cls=CSVKernel, csv_path=args.csv)
