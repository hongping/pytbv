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
from pytbv.kernels import CSVKernel
from pytbv.transaction import Transaction as CsvTrigger
from cocotb.triggers import Timer
import pyuvm
from pyuvm import *

class UvmTransaction(uvm_sequence_item):
    def __init__(self, name="transaction"):
        super().__init__(name)
        self.data = 0
        self.address = 0

    def __str__(self):
        return f"Address: 0x{self.address:x}, Data: 0x{self.data:x}"

class Producer(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
    
    def build_phase(self):
        self.put_port = uvm_blocking_put_port("put_port", self)

    async def run_phase(self):
        # Loop until simulation ends
        while True:
            self.logger.info(f"Waiting for CSV transaction")
            try:
                # Wait for trigger from CSV on Port "A"
                t = await CsvTrigger("A")
                
                # Create UVM transaction
                tr = UvmTransaction()
                tr.address = t.transaction.address
                tr.data = t.transaction.data
                
                self.logger.info(f"Received from CSV: {tr}")
                
                # Send to consumer
                await self.put_port.put(tr)
                
            except Exception as e:
                self.logger.error(f"Error waiting for transaction: {e}")


class Consumer(uvm_component):
    class producer_put_export(uvm_put_export):
        def __init__(self, name, parent):
            super().__init__(name, parent)
            self.parent = parent
        
        async def put(self, item):
            self.logger.info(f"Consuming transaction: {item}")
            self.parent.list.append(item)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.list = list()
    
    def build_phase(self):
        self.put_export = self.producer_put_export.create("put_export", self)

class Env(uvm_env):
    def build_phase(self):
        self.producer = Producer.create("producer", self)
        self.consumer = Consumer.create("consumer", self)
    
    def connect_phase(self):
        self.producer.put_port.connect(self.consumer.put_export)

@pyuvm.test()
class PyuvmCsvTest(uvm_test):
    def build_phase(self):
        self.env = Env("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        await Timer(200, "ns")
        self.drop_objection()


# Pytest wrapper to run via pytest
import pytest
@pytest.mark.integration
def test_pyuvm_csv_via_pytest():
    """Run pyuvm CSV test via pytest."""
    from pytbv.kernel import Kernel
    Kernel._inst = None  # Reset singleton
    result = run("tests.integration.test_pyuvm_csv", kernel_cls=CSVKernel, csv_path="tests/data/transactions.csv")
    assert result.all_passed, f"pyuvm CSV test failed: {result}"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="tests/data/transactions.csv")
    args = parser.parse_args()
    
    run("tests.integration.test_pyuvm_csv", kernel_cls=CSVKernel, csv_path=args.csv)
