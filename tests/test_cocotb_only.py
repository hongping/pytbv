from pytbv import run

import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_simple(dut):
    dut._log.info("start")
    await Timer(10, unit="ns")
    dut._log.info("end")

run("test_cocotb_only")
