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

"""
Unit tests for CSVKernel class in pytbv.kernels.csv module.
"""

import pytest
from pytbv.kernels.csv import CSVKernel, CbTransaction
from pytbv.kernel import Kernel


class TestCSVKernelInitialization:
    """Tests for CSVKernel initialization."""

    def test_csv_kernel_inherits_from_kernel(self, csv_kernel):
        """Verify CSVKernel is a subclass of Kernel."""
        assert isinstance(csv_kernel, Kernel)

    def test_csv_kernel_default_values(self, csv_kernel):
        """Verify CSVKernel has correct default values."""
        assert csv_kernel.product == "CSV Kernel"
        assert csv_kernel.transaction_listeners == {} or isinstance(csv_kernel.transaction_listeners, dict)

    def test_csv_kernel_loads_csv_on_init(self, csv_kernel):
        """Verify CSVKernel loads transactions from CSV during init."""
        assert len(csv_kernel.csv_events) == 3  # From fixture

    def test_csv_kernel_without_csv_path(self):
        """Verify CSVKernel can be created without csv_path."""
        kernel = CSVKernel()
        assert kernel.csv_events == []


class TestCSVKernelLoadTransactions:
    """Tests for CSVKernel.load_transactions method."""

    def test_load_transactions_parses_csv(self, sample_csv_file):
        """Verify load_transactions parses CSV file correctly."""
        kernel = CSVKernel()
        kernel.load_transactions(sample_csv_file)
        assert len(kernel.csv_events) == 3

    def test_load_transactions_validates_required_columns(self, invalid_csv_file):
        """Verify load_transactions raises error for missing Time/Port columns."""
        kernel = CSVKernel()
        with pytest.raises(ValueError, match="CSV must contain 'Time' and 'Port' columns"):
            kernel.load_transactions(invalid_csv_file)

    def test_load_transactions_sets_time_attribute(self, sample_csv_file):
        """Verify transactions have correct time attribute."""
        kernel = CSVKernel()
        kernel.load_transactions(sample_csv_file)
        times = [txn.time for txn in kernel.csv_events]
        assert times == [10, 20, 30]

    def test_load_transactions_sets_port_attribute(self, sample_csv_file):
        """Verify transactions have correct port attribute."""
        kernel = CSVKernel()
        kernel.load_transactions(sample_csv_file)
        ports = [txn.port for txn in kernel.csv_events]
        assert ports == ['A', 'A', 'B']

    def test_load_transactions_sorts_by_time(self, tmp_path):
        """Verify transactions are sorted by time after loading."""
        csv_file = tmp_path / "unsorted.csv"
        csv_file.write_text(
            "Time, Port, Data\n"
            "30, A, 1\n"
            "10, A, 2\n"
            "20, A, 3\n"
        )
        kernel = CSVKernel()
        kernel.load_transactions(str(csv_file))
        times = [txn.time for txn in kernel.csv_events]
        assert times == [10, 20, 30]

    def test_load_transactions_skips_past_events(self, tmp_path):
        """Verify transactions before current simulation_time are skipped."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "Time, Port, Data\n"
            "5, A, 1\n"
            "15, A, 2\n"
            "25, A, 3\n"
        )
        kernel = CSVKernel()
        kernel.simulation_time = 10
        kernel.load_transactions(str(csv_file))
        times = [txn.time for txn in kernel.csv_events]
        assert times == [15, 25]  # Time 5 is skipped


class TestDynamicTransaction:
    """Tests for DynamicTransaction attribute handling."""

    def test_dynamic_transaction_lowercase_attributes(self, sample_csv_file):
        """Verify DynamicTransaction has lowercase attribute access."""
        kernel = CSVKernel()
        kernel.load_transactions(sample_csv_file)
        txn = kernel.csv_events[0]
        assert txn.address == 0x100
        assert txn.data == 0xABCD

    def test_dynamic_transaction_original_case_attributes(self, sample_csv_file):
        """Verify DynamicTransaction preserves original case attributes."""
        kernel = CSVKernel()
        kernel.load_transactions(sample_csv_file)
        txn = kernel.csv_events[0]
        assert txn.Address == 0x100
        assert txn.Data == 0xABCD

    def test_dynamic_transaction_hex_conversion(self, sample_csv_file):
        """Verify hex strings are converted to integers."""
        kernel = CSVKernel()
        kernel.load_transactions(sample_csv_file)
        txn = kernel.csv_events[0]
        assert isinstance(txn.address, int)
        assert txn.address == 256  # 0x100

    def test_dynamic_transaction_repr(self, sample_csv_file):
        """Verify DynamicTransaction has a string representation."""
        kernel = CSVKernel()
        kernel.load_transactions(sample_csv_file)
        txn = kernel.csv_events[0]
        repr_str = repr(txn)
        assert isinstance(repr_str, str)


class TestCSVKernelCallbackRegistration:
    """Tests for CSVKernel transaction callback registration."""

    def test_register_transaction_callback_returns_cbtransaction(self, csv_kernel):
        """Verify register_transaction_callback returns CbTransaction."""
        cb = csv_kernel.register_transaction_callback("A", None, lambda ud: None, "data")
        assert isinstance(cb, CbTransaction)

    def test_register_transaction_callback_adds_listener(self, csv_kernel):
        """Verify callback is added to transaction_listeners."""
        cb = csv_kernel.register_transaction_callback("A", None, lambda ud: None, "data")
        assert len(csv_kernel.transaction_listeners["A"]) == 1
        assert cb in csv_kernel.transaction_listeners["A"]

    def test_register_multiple_callbacks_same_port(self, csv_kernel):
        """Verify multiple callbacks can be registered for same port."""
        csv_kernel.register_transaction_callback("A", None, lambda ud: None, "d1")
        csv_kernel.register_transaction_callback("A", None, lambda ud: None, "d2")
        assert len(csv_kernel.transaction_listeners["A"]) == 2


class TestCbTransaction:
    """Tests for CbTransaction class."""

    def test_cbtransaction_stores_attributes(self):
        """Verify CbTransaction stores port, transaction, cb, and ud."""
        cb_func = lambda ud: None
        cb = CbTransaction("A", "txn_obj", cb_func, "user_data")
        assert cb.port == "A"
        assert cb.transaction == "txn_obj"
        assert cb.cb is cb_func
        assert cb.ud == "user_data"

    def test_cbtransaction_callable_invokes_callback(self):
        """Verify calling CbTransaction invokes the callback with user data."""
        result = []
        cb = CbTransaction("A", None, lambda ud: result.append(ud), "test")
        cb()
        assert result == ["test"]

    def test_cbtransaction_deregister(self):
        """Verify deregister sets callback to None."""
        cb = CbTransaction("A", None, lambda ud: None, "data")
        cb.deregister()
        assert cb.cb is None


class TestCSVKernelRun:
    """Tests for CSVKernel run loop with CSV events."""

    def test_run_dispatches_csv_event_to_listener(self, csv_kernel):
        """Verify run() dispatches first CSV event to listener."""
        received = []
        
        class MockTrigger:
            transaction = None
        
        trigger = MockTrigger()
        csv_kernel.register_transaction_callback("A", None, lambda ud: received.append(ud.transaction), trigger)
        csv_kernel.run()
        
        # CSVKernel uses one-shot callbacks - listener is cleared after first dispatch
        # So we should receive exactly 1 transaction
        assert len(received) == 1
        assert received[0].time == 10

    def test_run_advances_to_csv_event_time(self, csv_kernel):
        """Verify simulation_time advances to CSV event time."""
        time_at_dispatch = []
        
        class MockTrigger:
            transaction = None
        
        def record_time(ud):
            time_at_dispatch.append(csv_kernel.simulation_time)
        
        trigger = MockTrigger()
        csv_kernel.register_transaction_callback("A", None, record_time, trigger)
        csv_kernel.run()
        
        # One-shot callback triggers at first event time
        assert time_at_dispatch == [10]

    def test_run_interleaves_timers_and_transactions(self, csv_kernel):
        """Verify both timer callbacks and CSV events are processed in time order."""
        events = []
        
        class MockTrigger:
            transaction = None
        
        trigger = MockTrigger()
        # Timer at time 5, before first CSV event at 10
        csv_kernel.register_timed_callback(5, lambda ud: events.append(('timer', 5)), None)
        csv_kernel.register_transaction_callback("A", None, lambda ud: events.append(('csv', csv_kernel.simulation_time)), trigger)
        csv_kernel.run()
        
        # Timer at 5 should come before CSV at 10
        assert events[0] == ('timer', 5)
        assert events[1] == ('csv', 10)

    def test_run_stops_when_no_events(self):
        """Verify run() exits when no callbacks or events remain."""
        kernel = CSVKernel()
        result = kernel.run()
        assert result is False

    def test_run_processes_multiple_listeners_same_port(self, csv_kernel):
        """Verify multiple listeners for same port all receive the event."""
        received = []
        
        class MockTrigger:
            transaction = None
        
        trigger1 = MockTrigger()
        trigger2 = MockTrigger()
        csv_kernel.register_transaction_callback("A", None, lambda ud: received.append('listener1'), trigger1)
        csv_kernel.register_transaction_callback("A", None, lambda ud: received.append('listener2'), trigger2)
        csv_kernel.run()
        
        assert 'listener1' in received
        assert 'listener2' in received
