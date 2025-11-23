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

import csv
import collections
import cocotb
from cocotb.triggers import GPITrigger
from pytbv.kernel import Kernel

class Transaction(GPITrigger):
    def __init__(self, port_name):
        super().__init__()
        self.port_name = port_name
        self._cbhdl = None

    def _prime(self, callback):
        if self._cbhdl is None:
            self._cbhdl = cocotb.simulator.register_transaction_callback(self.port_name, None, callback, self)
            if self._cbhdl is None:
                raise RuntimeError(f"Unable set up {self!s} Trigger")
        super()._prime(callback)

    def __repr__(self):
        return f"Transaction({self.port_name!r})"

class CbTransaction(object):
    def __init__(self, port, transaction, cb, ud):
        self.port = port
        self.transaction = transaction
        self.cb = cb
        self.ud = ud

    def __call__(self):
        if self.cb is not None:
            self.cb(self.ud)
    
    def deregister(self):
        self.cb = None

class CSVKernel(Kernel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.version = "0.0.1"
        self.product = "CSV Kernel"
        self.transaction_listeners = collections.defaultdict(list)
        self.csv_events = []
        
        if "csv_path" in kwargs:
            self.load_transactions(kwargs["csv_path"])
    
    def register_transaction_callback(self, port, txn, cb, ud):
        ret = CbTransaction(port, txn, cb, ud)
        self.transaction_listeners[port].append(ret)
        return ret

    def load_transactions(self, csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            for row in reader:
                # Ensure required columns exist
                if 'Time' not in row or 'Port' not in row:
                    raise ValueError("CSV must contain 'Time' and 'Port' columns")

                time = int(row['Time'])
                if time < self.simulation_time:
                    continue
                
                # Create a dynamic object for the transaction
                # We can use a simple class or just the dict itself.
                # Using a class allows attribute access (txn.Address) which existing tests might expect.
                class DynamicTransaction:
                    def __init__(self, data):
                        for k, v in data.items():
                            # Try to convert hex/int strings to integers
                            try:
                                setattr(self, k.lower(), int(v, 0))
                            except ValueError:
                                setattr(self, k.lower(), v)
                        # Also keep original keys
                        for k, v in data.items():
                             try:
                                setattr(self, k, int(v, 0))
                             except ValueError:
                                setattr(self, k, v)
                        
                    def __repr__(self):
                        return str(self.__dict__)

                txn_data = DynamicTransaction(row)
                
                # We need to attach the time and port specifically for the kernel to use
                # But we store the whole object in the event list
                # Let's wrap it or just add attributes
                txn_data.time = time
                txn_data.port = row['Port']
                
                self.csv_events.append(txn_data)
        
        # Sort by time
        self.csv_events.sort(key=lambda x: x.time)

    def run(self):
        while not self._stop_request:
            # Stop if no more cocotb callbacks (timers) AND no more transaction listeners
            if not self.scheduled_callbacks and not self.transaction_listeners:
                break

            next_timer_time = self.scheduled_callbacks[0].time_off if self.scheduled_callbacks else float('inf')
            next_csv_time = self.csv_events[0].time if self.csv_events else float('inf')
            
            next_event_time = min(next_timer_time, next_csv_time)
            
            if next_event_time == float('inf'):
                break

            self.simulation_time = next_event_time

            # Process CSV events at this time
            while self.csv_events and self.csv_events[0].time == self.simulation_time:
                txn = self.csv_events.pop(0)
                if txn.port in self.transaction_listeners:
                    # Swap out listeners list to handle re-registration during callbacks
                    listeners = self.transaction_listeners[txn.port]
                    self.transaction_listeners[txn.port] = []
                    
                    for listener in listeners:
                        listener.ud.transaction = txn
                        listener()

            # Process Timer events at this time
            while self.scheduled_callbacks and self.scheduled_callbacks[0].time_off == self.simulation_time:
                callback = self.scheduled_callbacks.pop(0)
                callback()
 
        return self._stop_request
