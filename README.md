# Python Transaction Based Verification (PyTBV)

## Overview

PyTBV is a Python-based testbench framework that enables execution of `cocotb` and `pyuvm` testbenches offline, without requiring a real HDL simulator. This approach is useful for unit testing, continuous integration, and rapid prototyping of verification logic.

The project is built upon concepts and code referenced from [cocotb-stub-sim](https://github.com/fvutils/cocotb-stub-sim) and [cocotb-vivado](https://github.com/themperek/cocotb-vivado).

## Status

**This project is currently in prototype stage.** The following features and limitations should be noted:

### Supported Features
- `cocotb.triggers.Timer` trigger support
- Basic testbench execution without hardware simulation

### Current Limitations
- Device Under Test (DUT) signal access is not yet implemented
- Limited trigger support beyond `Timer`

## Requirements

- **Python 3.12** or later (tested with Python 3.12)
- `cocotb` v2.0.0 or later
- `pyuvm` for UVM-based testbenches

## Installation

```bash
git clone https://github.com/hongping/pytbv.git pytbv
cd ./pytbv
pip3 install -e .
```

## Quick Start

Run the cocotb-only example:
```bash
python3 tests/integration/test_cocotb_only.py
```

Run the pyuvm example:
```bash
python3 tests/integration/test_basic_pyuvm.py
```

## Testing

PyTBV uses pytest for testing with separate unit and integration test suites.

### Install Development Dependencies

```bash
pip3 install -e ".[dev]"
```

### Run Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=pytbv --cov-report=html
```

### Run Integration Tests

Integration tests can be run via pytest or standalone:

```bash
# Via pytest (recommended)
pytest tests/integration/ -v -m integration

# Standalone execution
python3 tests/integration/test_cocotb_only.py
python3 tests/integration/test_basic_pyuvm.py
python3 tests/integration/test_csv_driver.py
```

## Example Output

```
> python3 tests/integration/test_cocotb_only.py 
     0.00ns INFO     cocotb                Running on python stub version 0.0.1
     0.00ns INFO     cocotb                Seeding Python random module with 1763109316
     0.00ns INFO     cocotb                Initialized cocotb v2.0.0 from .../.venv/lib/python3.12/site-packages/cocotb
     0.00ns INFO     cocotb.regression     pytest not found, install it to enable better AssertionError messages
     0.00ns INFO     cocotb                Running on python stub version 0.0.1
     0.00ns INFO     cocotb                Seeding Python random module with 1763109316
     0.00ns INFO     cocotb                Initialized cocotb v2.0.0 from .../.venv/lib/python3.12/site-packages/cocotb
     0.00ns INFO     cocotb.regression     pytest not found, install it to enable better AssertionError messages
     0.00ns INFO     cocotb                Running tests
     0.00ns INFO     cocotb.regression     running tests.integration.test_cocotb_only.test_simple (1/1)
     0.00ns INFO     cocotb.top            start
    10.00ns INFO     cocotb.top            end
    10.00ns INFO     cocotb.regression     tests.integration.test_cocotb_only.test_simple passed
    10.00ns INFO     cocotb.regression     **************************************************************************************
                                           ** TEST                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                           **************************************************************************************
                                           ** tests.integration.test_cocotb_only.test_simple   PASS          10.00           0.00      30977.13  **
                                           **************************************************************************************
                                           ** TESTS=1 PASS=1 FAIL=0 SKIP=0                 10.00           0.00       8274.42  **
                                           **************************************************************************************
                                                        
```


```
> python3 tests/integration/test_basic_pyuvm.py 
     0.00ns INFO     cocotb                             Running on python stub version 0.0.1
     0.00ns INFO     cocotb                             Seeding Python random module with 1763109521
     0.00ns INFO     cocotb                             Initialized cocotb v2.0.0 from .../.venv/lib/python3.12/site-packages/cocotb
     0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
     0.00ns INFO     cocotb                             Running tests
     0.00ns INFO     cocotb.regression                  running tests.integration.test_basic_pyuvm.hello_world (1/1)
     0.00ns INFO     ..bv/tests/test_basic_pyuvm.py(28) [uvm_test_top.env.producerA]: Producing transaction with data 0
     0.00ns INFO     ..bv/tests/test_basic_pyuvm.py(42) [uvm_test_top.env.consumer.producer_a_put_port]: Consuming transaction with data 0
     0.00ns INFO     ..bv/tests/test_basic_pyuvm.py(69) [uvm_test_top]: raised objection
     2.00ns INFO     ..bv/tests/test_basic_pyuvm.py(28) [uvm_test_top.env.producerA]: Producing transaction with data 1
     2.00ns INFO     ..bv/tests/test_basic_pyuvm.py(42) [uvm_test_top.env.consumer.producer_a_put_port]: Consuming transaction with data 1
     4.00ns INFO     ..bv/tests/test_basic_pyuvm.py(28) [uvm_test_top.env.producerA]: Producing transaction with data 2
     4.00ns INFO     ..bv/tests/test_basic_pyuvm.py(42) [uvm_test_top.env.consumer.producer_a_put_port]: Consuming transaction with data 2
     6.00ns INFO     ..bv/tests/test_basic_pyuvm.py(28) [uvm_test_top.env.producerA]: Producing transaction with data 3
     6.00ns INFO     ..bv/tests/test_basic_pyuvm.py(42) [uvm_test_top.env.consumer.producer_a_put_port]: Consuming transaction with data 3
     8.00ns INFO     ..bv/tests/test_basic_pyuvm.py(28) [uvm_test_top.env.producerA]: Producing transaction with data 4
     8.00ns INFO     ..bv/tests/test_basic_pyuvm.py(42) [uvm_test_top.env.consumer.producer_a_put_port]: Consuming transaction with data 4
    50.00ns INFO     ..bv/tests/test_basic_pyuvm.py(71) [uvm_test_top]: going to drop objection
    50.00ns INFO     cocotb.regression                  tests.integration.test_basic_pyuvm.hello_world passed
    50.00ns INFO     cocotb.regression                  **************************************************************************************
                                                        ** TEST                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                                        **************************************************************************************
                                                        ** tests.integration.test_basic_pyuvm.hello_world   PASS          50.00           0.00      18339.76  **
                                                        **************************************************************************************
                                                        ** TESTS=1 PASS=1 FAIL=0 SKIP=0                 50.00           0.01       9950.90  **
                                                        **************************************************************************************
```