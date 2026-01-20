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
Unit tests for the simulator module (cocotb.simulator replacement).
"""

import pytest
from unittest.mock import MagicMock, patch


class TestSimulatorDelegation:
    """Tests for simulator module delegation to Kernel."""

    def test_get_simulator_product_delegates_to_kernel(self, kernel):
        """Verify get_simulator_product delegates to Kernel.inst()."""
        from pytbv.kernel import Kernel
        Kernel._inst = kernel
        
        from pytbv import simulator
        result = simulator.get_simulator_product()
        assert result == kernel.get_simulator_product()

    def test_get_simulator_version_delegates_to_kernel(self, kernel):
        """Verify get_simulator_version delegates to Kernel.inst()."""
        from pytbv.kernel import Kernel
        Kernel._inst = kernel
        
        from pytbv import simulator
        result = simulator.get_simulator_version()
        assert result == kernel.get_simulator_version()

    def test_get_sim_time_delegates_to_kernel(self, kernel):
        """Verify get_sim_time delegates to Kernel.inst()."""
        from pytbv.kernel import Kernel
        Kernel._inst = kernel
        kernel.simulation_time = 12345
        
        from pytbv import simulator
        result = simulator.get_sim_time()
        assert result == kernel.get_sim_time()

    def test_get_root_handle_delegates_to_kernel(self, kernel):
        """Verify get_root_handle delegates to Kernel.inst()."""
        from pytbv.kernel import Kernel
        Kernel._inst = kernel
        
        from pytbv import simulator
        result = simulator.get_root_handle(None)
        expected = kernel.get_root_handle()
        assert result.simobject is expected.simobject

    def test_get_precision_returns_kernel_precision(self, kernel):
        """Verify get_precision returns Kernel.inst().precision."""
        from pytbv.kernel import Kernel
        Kernel._inst = kernel
        kernel.precision = -12
        
        from pytbv import simulator
        result = simulator.get_precision()
        assert result == -12

    def test_stop_simulator_delegates_to_kernel(self, kernel):
        """Verify stop_simulator delegates to Kernel.inst()."""
        from pytbv.kernel import Kernel
        Kernel._inst = kernel
        
        from pytbv import simulator
        simulator.stop_simulator()
        assert kernel._stop_request is True

    def test_register_timed_callback_delegates_to_kernel(self, kernel):
        """Verify register_timed_callback delegates to Kernel.inst()."""
        from pytbv.kernel import Kernel, CbTimed
        Kernel._inst = kernel
        
        from pytbv import simulator
        cb_func = lambda ud: None
        result = simulator.register_timed_callback(100, cb_func, "data")
        
        assert isinstance(result, CbTimed)
        assert result in kernel.scheduled_callbacks


class TestSimulatorNoOps:
    """Tests for simulator no-op functions."""

    def test_set_sim_event_callback_noop(self):
        """Verify set_sim_event_callback is a no-op."""
        from pytbv import simulator
        # Should not raise
        result = simulator.set_sim_event_callback(None)
        assert result is None

    def test_initialize_logger_noop(self):
        """Verify initialize_logger is a no-op."""
        from pytbv import simulator
        result = simulator.initialize_logger(None, None)
        assert result is None

    def test_package_iterate_noop(self):
        """Verify package_iterate is a no-op."""
        from pytbv import simulator
        result = simulator.package_iterate()
        assert result is None

    def test_set_gpi_log_level_noop(self):
        """Verify set_gpi_log_level is a no-op."""
        from pytbv import simulator
        result = simulator.set_gpi_log_level(0)
        assert result is None


class TestSimulatorGetattr:
    """Tests for simulator __getattr__ fallback."""

    def test_getattr_delegates_to_kernel(self, kernel):
        """Verify __getattr__ delegates unknown attributes to Kernel.inst()."""
        from pytbv.kernel import Kernel
        Kernel._inst = kernel
        kernel.custom_attr = "custom_value"
        
        from pytbv import simulator
        result = simulator.custom_attr
        assert result == "custom_value"
