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

from cocotb.triggers import Timer

import pyuvm
from pyuvm import *
import pytest

class Transaction(uvm_sequence_item):
    def __init__(self, name="transaction"):
        super().__init__(name)
        self.data = 0
        self.address = 0


class Producer(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
    
    def build_phase(self):
        self.put_port = uvm_blocking_put_port("put_port", self)

    async def run_phase(self):
        self.raise_objection()

        for i in range(5):
            tr = Transaction()
            tr.data = i
            self.logger.info(f"Producing transaction with data {tr.data}")
            await self.put_port.put(tr)
            await Timer(2, "ns")
        
        self.drop_objection()


class Consumer(uvm_component):
    class producer_a_put(uvm_put_export):
        def __init__(self, name, parent):
            super().__init__(name, parent)
            self.parent = parent
        
        async def put(self, item):
            self.logger.info(f"Consuming transaction with data {item.data}")
            self.parent.list.append(item)

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.list = list()
    
    def build_phase(self):
        self.producer_a_put_port = self.producer_a_put.create("producer_a_put_port", self)

            
class Env(uvm_env):
    def build_phase(self):
        self.producerA = Producer.create("producerA", self)
        self.consumer = Consumer.create("consumer", self)
    
    def connect_phase(self):
        self.producerA.put_port.connect(self.consumer.producer_a_put_port)


@pyuvm.test()
class hello_world(uvm_test):
    def build_phase(self):
        self.env = Env("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        self.logger.info("raised objection")
        await Timer(50, "ns")
        self.logger.info("going to drop objection")
        self.drop_objection()


# Pytest wrapper to run via pytest
@pytest.mark.integration
def test_basic_pyuvm_via_pytest():
    """Run pyuvm test via pytest."""
    from pytbv.kernel import Kernel
    Kernel._inst = None  # Reset singleton
    result = run("tests.integration.test_basic_pyuvm")
    assert result.all_passed, f"pyuvm test failed: {result}"


if __name__ == "__main__":
    run("tests.integration.test_basic_pyuvm")
