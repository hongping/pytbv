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

import collections
from vcdvcd import VCDVCD
from pytbv.kernel import Kernel
from pytbv.transaction import CbTransaction

class WaveKernel(Kernel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.version = "0.0.1"
        self.product = "Wave Kernel"
        self.transaction_listeners = collections.defaultdict(list)
        self.wave_events = []

        if "vcd_path" in kwargs:
            self.load_waves(kwargs["vcd_path"])

    def register_transaction_callback(self, port, txn, cb, ud):
        ret = CbTransaction(port, txn, cb, ud)
        self.transaction_listeners[port].append(ret)
        return ret

    def load_waves(self, vcd_path):
        vcd = VCDVCD(vcd_path)
        # Iterate over signal names and access data via dictionary-like lookup
        for signal_name in vcd.references_to_ids.keys():
            signal_data = vcd[signal_name]
            for timestamp, value in signal_data.tv:
                self.wave_events.append({
                    "time": timestamp,
                    "port": signal_name,
                    "value": value
                })
        
        # Sort by time
        self.wave_events.sort(key=lambda x: x["time"])

    def run(self):
        while not self._stop_request:
            if not self.scheduled_callbacks and not self.transaction_listeners:
                break

            next_timer_time = self.scheduled_callbacks[0].time_off if self.scheduled_callbacks else float('inf')
            next_wave_time = self.wave_events[0]["time"] if self.wave_events else float('inf')
            
            next_event_time = min(next_timer_time, next_wave_time)
            
            if next_event_time == float('inf'):
                break

            self.simulation_time = next_event_time

            # Process Wave events at this time
            while self.wave_events and self.wave_events[0]["time"] == self.simulation_time:
                event = self.wave_events.pop(0)
                if event["port"] in self.transaction_listeners:
                    listeners = self.transaction_listeners[event["port"]]
                    self.transaction_listeners[event["port"]] = []
                    
                    for listener in listeners:
                        # Create a simple object for the transaction
                        class WaveTransaction:
                            def __init__(self, data):
                                for k, v in data.items():
                                    setattr(self, k, v)
                        
                        listener.ud.transaction = WaveTransaction(event)
                        listener()

            # Process Timer events at this time
            while self.scheduled_callbacks and self.scheduled_callbacks[0].time_off == self.simulation_time:
                callback = self.scheduled_callbacks.pop(0)
                callback()
 
        return self._stop_request