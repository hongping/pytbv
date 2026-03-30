
from pytbv import run
from pytbv.kernels import CSVKernel, Transaction as CsvTrigger
import pyuvm
from pyuvm import *
import cocotb
from cocotb.triggers import Timer
import random

# 1. Transaction Item
class AdderTransaction(uvm_sequence_item):
    def __init__(self, name="AdderTransaction", a=0, b=0, sum=None):
        super().__init__(name)
        self.a = a
        self.b = b
        self.sum = sum

    def __str__(self):
        return f"a={self.a}, b={self.b}, sum={self.sum}"

# 2. Sequencer
class AdderSequencer(uvm_sequencer):
    pass

# 3. Driver
class Driver(uvm_driver):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

    async def run_phase(self):
        while True:
            txn = await self.seq_item_port.get_next_item()
            self.logger.info(f"Driving: {txn}")
            # In a real scenario, this would drive DUT signals.
            # Here, we just send it to the scoreboard.
            self.ap.write(txn)
            self.seq_item_port.item_done()

# 4. Monitor
class Monitor(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.ap = uvm_analysis_port("ap", self)

    async def run_phase(self):
        while True:
            try:
                # Wait for a transaction from the 'out' port of the CSV
                csv_txn = await CsvTrigger("out")
                sum_val = int(csv_txn.transaction.sum)
                self.logger.info(f"Monitor saw sum: {sum_val}")
                
                # Create a transaction and send it for checking
                mon_txn = AdderTransaction(sum=sum_val)
                self.ap.write(mon_txn)
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                break

# 5. Agent
class AdderAgent(uvm_agent):
    def build_phase(self):
        self.sequencer = AdderSequencer.create("sequencer", self)
        self.driver = Driver.create("driver", self)
        self.monitor = Monitor.create("monitor", self)
        self.ap = uvm_analysis_port("ap", self) # For the driver
        self.mon_ap = uvm_analysis_port("mon_ap", self) # For the monitor

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
        self.driver.ap.connect(self.ap)
        self.monitor.ap.connect(self.mon_ap)

# 6. Scoreboard
class Scoreboard(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.driver_imp = uvm_export_base("driver_imp", self)
        self.monitor_imp = uvm_export_base("monitor_imp", self)
        self.driver_queue = []
        self.errors = 0
        self.passed = 0

    def build_phase(self):
        self.driver_imp.write = self.write_driver
        self.monitor_imp.write = self.write_monitor

    def write_driver(self, txn):
        self.logger.info(f"Scoreboard got from driver: {txn}")
        self.driver_queue.append(txn)

    def write_monitor(self, mon_txn):
        self.logger.info(f"Scoreboard got from monitor: {mon_txn}")
        if not self.driver_queue:
            self.logger.error("Received monitor data with no waiting driver data.")
            self.errors += 1
            return

        drv_txn = self.driver_queue.pop(0)
        expected_sum = drv_txn.a + drv_txn.b
        if mon_txn.sum == expected_sum:
            self.logger.info(f"PASS: {drv_txn.a} + {drv_txn.b} = {mon_txn.sum}")
            self.passed += 1
        else:
            self.logger.error(f"FAIL: {drv_txn.a} + {drv_txn.b} = {expected_sum}, but got {mon_txn.sum}")
            self.errors += 1

    def final_phase(self):
        if self.errors == 0 and self.passed > 0:
            self.logger.info(f"Final check PASSED: {self.passed} transactions verified.")
        else:
            self.logger.error(f"Final check FAILED: {self.errors} errors, {self.passed} passed.")
        assert self.errors == 0

# 7. Environment
class AdderEnv(uvm_env):
    def build_phase(self):
        self.agent = AdderAgent.create("agent", self)
        self.scoreboard = Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.agent.ap.connect(self.scoreboard.driver_imp)
        self.agent.mon_ap.connect(self.scoreboard.monitor_imp)

# 8. Sequence
class AdderSequence(uvm_sequence):
    async def body(self):
        # The number of transactions is dictated by the CSV file
        for _ in range(3): 
            # First, get the stimulus from the CSV 'in' port
            csv_in = await CsvTrigger("in")
            a = int(csv_in.transaction.a)
            b = int(csv_in.transaction.b)
            
            # Now create a transaction with that stimulus
            txn = AdderTransaction(a=a, b=b)
            await self.start_item(txn)
            # self.logger.info(f"Sequence got from CSV: a={a}, b={b}")
            await self.finish_item(txn)

# 9. Test
@pyuvm.test()
class TestSimpleAdder(uvm_test):
    def build_phase(self):
        self.env = AdderEnv.create("env", self)

    async def run_phase(self):
        self.raise_objection()
        seq = AdderSequence()
        await seq.start(self.env.agent.sequencer)
        await Timer(100, "ns") # Allow time for all CSV transactions
        self.drop_objection()

# 10. Main execution block
if __name__ == "__main__":
    run(
        "tests.test_simple_adder",
        kernel_cls=CSVKernel,
        csv_path="tests/adder_transactions.csv"
    )
