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
Unit tests for helper classes: SimObject, gpi_sim_hdl, CbTimed.
"""

import pytest
from pytbv.kernel import SimObject, gpi_sim_hdl, CbTimed, Kernel
from pytbv.gpi_constants import MODULE


class TestSimObject:
    """Tests for SimObject class."""

    def test_simobject_stores_kernel(self, kernel):
        """Verify SimObject stores reference to kernel."""
        obj = SimObject(kernel, "test_obj")
        assert obj.kernel is kernel

    def test_simobject_stores_name(self, kernel):
        """Verify SimObject stores the provided name."""
        obj = SimObject(kernel, "my_module")
        assert obj.name == "my_module"


class TestGpiSimHdl:
    """Tests for gpi_sim_hdl class."""

    def test_gpi_sim_hdl_stores_simobject(self, kernel):
        """Verify gpi_sim_hdl wraps a SimObject."""
        obj = SimObject(kernel, "test")
        handle = gpi_sim_hdl(obj)
        assert handle.simobject is obj

    def test_get_type_returns_module(self, kernel):
        """Verify get_type returns MODULE constant."""
        obj = SimObject(kernel, "test")
        handle = gpi_sim_hdl(obj)
        assert handle.get_type() == MODULE

    def test_get_type_string_returns_module(self, kernel):
        """Verify get_type_string returns 'module'."""
        obj = SimObject(kernel, "test")
        handle = gpi_sim_hdl(obj)
        assert handle.get_type_string() == "module"

    def test_get_name_string_returns_simobject_name(self, kernel):
        """Verify get_name_string returns the SimObject's name."""
        obj = SimObject(kernel, "my_dut")
        handle = gpi_sim_hdl(obj)
        assert handle.get_name_string() == "my_dut"

    def test_get_definition_name_returns_class_name(self, kernel):
        """Verify get_definition_name returns the class name."""
        obj = SimObject(kernel, "test")
        handle = gpi_sim_hdl(obj)
        assert handle.get_definition_name() == "SimObject"

    def test_get_definition_file_returns_module_file(self, kernel):
        """Verify get_definition_file returns the module file path."""
        obj = SimObject(kernel, "test")
        handle = gpi_sim_hdl(obj)
        file_path = handle.get_definition_file()
        assert file_path is not None
        assert "kernel.py" in file_path


class TestCbTimed:
    """Tests for CbTimed callback class."""

    def test_cbtimed_stores_attributes(self):
        """Verify CbTimed stores time_off, cb, and ud."""
        cb_func = lambda ud: None
        cb = CbTimed(100, cb_func, "user_data")
        assert cb.time_off == 100
        assert cb.cb is cb_func
        assert cb.ud == "user_data"

    def test_cbtimed_callable_invokes_callback(self):
        """Verify calling CbTimed invokes the callback with user data."""
        result = []
        cb = CbTimed(10, lambda ud: result.append(ud), "test_value")
        cb()
        assert result == ["test_value"]

    def test_cbtimed_callable_with_none_callback(self):
        """Verify calling CbTimed with None callback does nothing."""
        cb = CbTimed(10, None, "data")
        # Should not raise
        cb()

    def test_cbtimed_deregister_nullifies_callback(self):
        """Verify deregister() sets callback to None."""
        cb = CbTimed(10, lambda ud: None, "data")
        assert cb.cb is not None
        cb.deregister()
        assert cb.cb is None

    def test_cbtimed_deregistered_noop(self):
        """Verify deregistered CbTimed does nothing when called."""
        result = []
        cb = CbTimed(10, lambda ud: result.append(ud), "value")
        cb.deregister()
        cb()
        assert result == []  # Callback was not invoked
