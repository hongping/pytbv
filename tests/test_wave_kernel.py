from pytbv import run
from pytbv.kernels import WaveKernel
from pytbv.transaction import Transaction
import cocotb

async def run_test(dut):
    results = []
    expected = [
        {'port': 'top.a', 'value': '0'},
        {'port': 'top.b', 'value': '1'},
        {'port': 'top.a', 'value': '1'},
        {'port': 'top.b', 'value': '0'},
        {'port': 'top.a', 'value': '0'},
        {'port': 'top.b', 'value': '1'},
    ]

    # This test relies on the kernel processing events in order.
    # A more robust test would check timestamps.
    for i in range(len(expected)):
        t = await Transaction(expected[i]['port'])
        results.append({'port': t.transaction.port, 'value': t.transaction.value})
        # Await a transaction on a specific port
        if i < len(expected) -1:
            await cocotb.triggers.NullTrigger() # Yield to allow other monitors to run

    dut._log.info(f"Collected {len(results)} transactions.")
    
    # The order of events is guaranteed by the kernel's run loop, so direct comparison is fine.
    assert results == expected

@cocotb.test()
async def test_wave_kernel(dut):
    cocotb.start_soon(run_test(dut))
    # The run() function in __main__ will drive the kernel
    # This test just needs to start the process and can finish
    await cocotb.triggers.Timer(1, "ns")


if __name__ == "__main__":
    run("tests.test_wave_kernel", kernel_cls=WaveKernel, vcd_path="tests/sample.vcd")
