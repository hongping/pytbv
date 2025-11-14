from pytbv import run

from cocotb.triggers import Timer

import pyuvm
from pyuvm import *

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


if __name__ == "__main__":
    run("test_basic_pyuvm")
