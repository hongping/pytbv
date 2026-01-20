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
Unit tests for the Kernel class in pytbv.kernel module.
"""

import pytest
from pytbv.kernel import Kernel, SimObject, gpi_sim_hdl, CbTimed
from pytbv.gpi_constants import MODULE


class TestKernelInitialization:
    """Tests for Kernel initialization and default state."""

    def test_kernel_initialization_defaults(self, kernel):
        """Verify Kernel initializes with correct default values."""
        assert kernel.simulation_time == 0
        assert kernel.precision == -9
        assert kernel.scheduled_callbacks == []
        assert kernel._stop_request is False

    def test_kernel_has_root_simobject(self, kernel):
        """Verify Kernel creates a root SimObject named 'top'."""
        assert isinstance(kernel.root, SimObject)
        assert kernel.root.name == "top"
        assert kernel.root.kernel is kernel


class TestKernelSingleton:
    """Tests for Kernel singleton pattern."""

    def test_kernel_singleton_pattern(self):
        """Verify Kernel.inst() returns the same instance."""
        inst1 = Kernel.inst()
        inst2 = Kernel.inst()
        assert inst1 is inst2

    def test_kernel_init_creates_new_instance(self):
        """Verify Kernel.init() creates a new singleton instance."""
        old_inst = Kernel.inst()
        new_inst = Kernel.init()
        assert new_inst is not old_inst
        assert Kernel.inst() is new_inst

    def test_kernel_init_with_kwargs(self):
        """Verify Kernel.init() passes kwargs to constructor."""
        # Create a subclass to verify kwargs are passed
        class CustomKernel(Kernel):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.custom_param = kwargs.get('custom_param', None)
        
        inst = CustomKernel.init(custom_param='test_value')
        assert inst.custom_param == 'test_value'


class TestKernelGetters:
    """Tests for Kernel getter methods."""

    def test_get_root_handle_returns_gpi_sim_hdl(self, kernel):
        """Verify get_root_handle returns a gpi_sim_hdl wrapping root."""
        handle = kernel.get_root_handle()
        assert isinstance(handle, gpi_sim_hdl)
        assert handle.simobject is kernel.root

    def test_get_sim_time_at_zero(self, kernel):
        """Verify get_sim_time returns (0, 0) at initialization."""
        high, low = kernel.get_sim_time()
        assert high == 0
        assert low == 0

    def test_get_sim_time_low_bits(self, kernel):
        """Verify get_sim_time correctly returns low 32 bits."""
        kernel.simulation_time = 0xDEADBEEF
        high, low = kernel.get_sim_time()
        assert low == 0xDEADBEEF
        assert high == 0

    def test_get_sim_time_high_bits(self, kernel):
        """Verify get_sim_time correctly splits high and low 32-bit values."""
        kernel.simulation_time = 0x1_FFFFFFFF  # 33-bit value
        high, low = kernel.get_sim_time()
        assert high == 1
        assert low == 0xFFFFFFFF


class TestKernelCallbackRegistration:
    """Tests for Kernel callback registration and ordering."""

    def test_register_timed_callback_returns_cbtimed(self, kernel):
        """Verify register_timed_callback returns a CbTimed object."""
        cb = kernel.register_timed_callback(100, lambda ud: None, None)
        assert isinstance(cb, CbTimed)

    def test_register_timed_callback_adds_to_queue(self, kernel):
        """Verify callback is added to scheduled_callbacks."""
        cb = kernel.register_timed_callback(100, lambda ud: None, None)
        assert cb in kernel.scheduled_callbacks

    def test_callback_ordering_single(self, kernel):
        """Verify single callback is scheduled correctly."""
        kernel.register_timed_callback(100, lambda ud: None, None)
        assert len(kernel.scheduled_callbacks) == 1
        assert kernel.scheduled_callbacks[0].time_off == 100

    def test_callback_ordering_multiple_ascending(self, kernel):
        """Verify callbacks are ordered when registered in ascending order."""
        kernel.register_timed_callback(100, lambda ud: None, None)
        kernel.register_timed_callback(200, lambda ud: None, None)
        kernel.register_timed_callback(300, lambda ud: None, None)
        
        times = [cb.time_off for cb in kernel.scheduled_callbacks]
        assert times == [100, 200, 300]

    def test_callback_ordering_multiple_descending(self, kernel):
        """Verify callbacks are reordered when registered in descending order."""
        kernel.register_timed_callback(300, lambda ud: None, None)
        kernel.register_timed_callback(200, lambda ud: None, None)
        kernel.register_timed_callback(100, lambda ud: None, None)
        
        times = [cb.time_off for cb in kernel.scheduled_callbacks]
        assert times == [100, 200, 300]

    def test_callback_ordering_mixed(self, kernel):
        """Verify callbacks are correctly ordered with mixed registration."""
        kernel.register_timed_callback(200, lambda ud: None, None)
        kernel.register_timed_callback(100, lambda ud: None, None)
        kernel.register_timed_callback(300, lambda ud: None, None)
        kernel.register_timed_callback(150, lambda ud: None, None)
        
        times = [cb.time_off for cb in kernel.scheduled_callbacks]
        assert times == [100, 150, 200, 300]

    def test_callback_absolute_time_from_current(self, kernel):
        """Verify callback time is calculated relative to current simulation time."""
        kernel.simulation_time = 50
        cb = kernel.register_timed_callback(100, lambda ud: None, None)
        assert cb.time_off == 150  # 50 + 100


class TestKernelRun:
    """Tests for Kernel run loop execution."""

    def test_run_stops_when_no_callbacks(self, kernel):
        """Verify run() returns when callback queue is empty."""
        result = kernel.run()
        assert result is False  # Not stopped by stop_request

    def test_run_executes_callback(self, kernel):
        """Verify run() executes scheduled callbacks."""
        executed = []
        kernel.register_timed_callback(10, lambda ud: executed.append(ud), 'test')
        kernel.run()
        assert executed == ['test']

    def test_run_executes_callbacks_in_order(self, kernel):
        """Verify callbacks are executed in correct time order."""
        execution_order = []
        kernel.register_timed_callback(30, lambda ud: execution_order.append(ud), 'third')
        kernel.register_timed_callback(10, lambda ud: execution_order.append(ud), 'first')
        kernel.register_timed_callback(20, lambda ud: execution_order.append(ud), 'second')
        kernel.run()
        assert execution_order == ['first', 'second', 'third']

    def test_run_advances_simulation_time(self, kernel):
        """Verify simulation_time advances to callback times."""
        times_at_execution = []
        def record_time(ud):
            times_at_execution.append(kernel.simulation_time)
        
        kernel.register_timed_callback(10, record_time, None)
        kernel.register_timed_callback(50, record_time, None)
        kernel.run()
        
        assert times_at_execution == [10, 50]

    def test_run_stops_on_stop_request(self, kernel):
        """Verify run() stops when stop_simulator() is called."""
        def stop_callback(ud):
            kernel.stop_simulator()
        
        kernel.register_timed_callback(10, stop_callback, None)
        kernel.register_timed_callback(100, lambda ud: None, 'should_not_run')
        
        result = kernel.run()
        assert result is True  # Stopped by stop_request
        assert kernel.simulation_time == 10  # Stopped at first callback

    def test_stop_simulator_sets_flag(self, kernel):
        """Verify stop_simulator() sets _stop_request flag."""
        assert kernel._stop_request is False
        kernel.stop_simulator()
        assert kernel._stop_request is True

    def test_run_executes_multiple_callbacks_at_same_time(self, kernel):
        """Verify multiple callbacks at the same time are all executed."""
        executed = []
        kernel.register_timed_callback(10, lambda ud: executed.append('a'), None)
        kernel.register_timed_callback(10, lambda ud: executed.append('b'), None)
        kernel.register_timed_callback(10, lambda ud: executed.append('c'), None)
        kernel.run()
        
        assert len(executed) == 3
        assert set(executed) == {'a', 'b', 'c'}
