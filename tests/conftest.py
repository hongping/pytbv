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
Pytest configuration and shared fixtures for pytbv tests.
"""

import pytest
import sys


@pytest.fixture(autouse=True)
def reset_kernel_singleton():
    """Reset Kernel singleton before each test to ensure isolation."""
    from pytbv.kernel import Kernel
    Kernel._inst = None
    yield
    Kernel._inst = None


@pytest.fixture
def kernel():
    """Provide a fresh Kernel instance."""
    from pytbv.kernel import Kernel
    return Kernel()


@pytest.fixture
def csv_kernel(tmp_path):
    """
    Provide a fresh CSVKernel instance with a temporary CSV file.
    """
    from pytbv.kernels.csv import CSVKernel
    
    # Create a sample CSV file
    csv_file = tmp_path / "test_transactions.csv"
    csv_file.write_text(
        "Time, Port, Address, Data, Status\n"
        "10, A, 0x100, 0xABCD, 0x0\n"
        "20, A, 0x200, 0xDEAD, 0x1\n"
        "30, B, 0x300, 0xBEEF, 0x2\n"
    )
    
    return CSVKernel(csv_path=str(csv_file))


@pytest.fixture
def sample_csv_file(tmp_path):
    """Provide a sample CSV file path for testing."""
    csv_file = tmp_path / "transactions.csv"
    csv_file.write_text(
        "Time, Port, Address, Data, Status\n"
        "10, A, 0x100, 0xABCD, 0x0\n"
        "20, A, 0x200, 0xDEAD, 0x1\n"
        "30, B, 0x300, 0xBEEF, 0x2\n"
    )
    return str(csv_file)


@pytest.fixture
def invalid_csv_file(tmp_path):
    """Provide an invalid CSV file (missing required columns)."""
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(
        "Name, Value\n"
        "foo, 123\n"
    )
    return str(csv_file)
