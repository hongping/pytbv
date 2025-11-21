from pytbv import run

import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_simple(dut):
    dut._log.info("start")
    await Timer(10, unit="ns")
    dut._log.info("end")


if __name__ == "__main__":
    run("test_cocotb_only")
