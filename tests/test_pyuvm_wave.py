
import cocotb
from pytbv import run
from pytbv.kernels import WaveKernel
from pytbv.transaction import Transaction as WaveTrigger
from cocotb.triggers import Timer
import pyuvm
from pyuvm import *

# 1. High-Level Transaction
class BusPacket(uvm_sequence_item):
    def __init__(self, name="bus_packet"):
        super().__init__(name)
        self.addr = 0
        self.data = 0

    def __str__(self):
        return f"Addr: 0x{self.addr:x}, Data: 0x{self.data:x}"

    def __eq__(self, other):
        return self.addr == other.addr and self.data == other.data

# 2. Monitor
# Reads VCD signals, tracks state, and publishes BusPackets on Valid
class BusMonitor(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.ap = uvm_analysis_port("ap", self)
        
        # Internal state tracking for signals
        # We need to explicitly initialize because WaveKernel only sends CHANGE events
        # We assume 0 at start as per VCD generator
        self.signals = {
            "top.clk": 0,
            "top.valid": 0,
            "top.addr": 0,
            "top.data": 0
        }

    async def run_phase(self):
        # Start listeners for all signals we care about
        for sig in self.signals.keys():
            cocotb.start_soon(self.track_signal(sig))

        # Main Protocol Loop
        # Wait for Posedge Clock
        while True:
            # We track the clock change via our state tracker, but we also want to wake up
            # accurately when it happens. 
            # We can just wait for the clock trigger here.
            t = await WaveTrigger("top.clk")
            curr_val = int(t.transaction.value)
            
            if curr_val == 1: # Rising Edge
                # Sample signals
                # Note: In a real simulator, values settle before posedge. 
                # Our VCD generator updates on negedge, so values are stable at posedge.
                
                # Check Valid
                if self.signals["top.valid"] == 1:
                    pkt = BusPacket("pkt")
                    pkt.addr = self.signals["top.addr"]
                    pkt.data = self.signals["top.data"]
                    
                    self.logger.info(f"Monitor sampled: {pkt}")
                    self.ap.write(pkt)

    async def track_signal(self, name):
        """
        Continuously waits for changes on 'name' and updates internal state.
        This provides a 'current value' mechanism for the Wave Kernel.
        """
        while True:
            t = await WaveTrigger(name)
            # Update state
            # WaveKernel values are strings mostly, VCD parser returns strings or ints?
            # VCDVCD parser returns values. For binary it's '0' or '1'.
            # For vectors it might be int or string.
            val = t.transaction.value
            
            # Convert to int if possible
            try:
                if isinstance(val, str):
                   # VCD values are typically binary strings
                   # Check if it has 'b' prefix (vcdvcd usually strips it or returns raw)
                   # Based on debug output, it returns '10000' etc.
                   if val.startswith('b'): 
                        val = int(val[1:], 2)
                   else:
                        # Assume binary if not prefixed, because digital signals
                        # But be careful of '1' and '0' which are valid in any base
                        val = int(val, 2)
                self.signals[name] = val
            except ValueError:
                self.signals[name] = 0 # Fallback for X/Z etc

# 3. Scoreboard
class AnalysisQueueExport(uvm_analysis_export):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.q = cocotb.queue.Queue()
    def write(self, item):
        self.q.put_nowait(item)

class Scoreboard(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
    def build_phase(self):
        self.export = AnalysisQueueExport("export", self)
        
    async def run_phase(self):
        # Expected sequence from generate_vcd.py
        expected = [
            (0x10, 0xAA),
            (0x20, 0xBB),
            (0x30, 0xCC)
        ]
        
        idx = 0
        while True:
            pkt = await self.export.q.get()
            self.logger.info(f"Scoreboard received: {pkt}")
            
            if idx < len(expected):
                exp_addr, exp_data = expected[idx]
                if pkt.addr == exp_addr and pkt.data == exp_data:
                    self.logger.info(f"MATCH: {pkt}")
                else:
                    self.logger.error(f"MISMATCH: Expected Addr={exp_addr:x} Data={exp_data:x}, Got {pkt}")
                idx += 1
            else:
                self.logger.warning(f"Extra packet: {pkt}")

# 4. Env & Test
class Env(uvm_env):
    def build_phase(self):
        self.monitor = BusMonitor("monitor", self)
        self.scoreboard = Scoreboard("scoreboard", self)
    
    def connect_phase(self):
        self.monitor.ap.connect(self.scoreboard.export)

@pyuvm.test()
class TestBusProtocol(uvm_test):
    def build_phase(self):
        self.env = Env("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        await Timer(200, "ns")
        self.drop_objection()

if __name__ == "__main__":
    run("tests.test_pyuvm_wave", kernel_cls=WaveKernel, vcd_path="tests/bus_protocol.vcd")
