import cocotb
from cocotb.triggers import GPITrigger

class Transaction(GPITrigger):
    def __init__(self, port_name):
        super().__init__()
        self.port_name = port_name
        self._cbhdl = None

    def _prime(self, callback):
        if self._cbhdl is None:
            self._cbhdl = cocotb.simulator.register_transaction_callback(self.port_name, None, callback, self)
            if self._cbhdl is None:
                raise RuntimeError(f"Unable set up {self!s} Trigger")
        super()._prime(callback)

    def __repr__(self):
        return f"Transaction({self.port_name!r})"

class CbTransaction(object):
    def __init__(self, port, transaction, cb, ud):
        self.port = port
        self.transaction = transaction
        self.cb = cb
        self.ud = ud

    def __call__(self):
        if self.cb is not None:
            self.cb(self.ud)
    
    def deregister(self):
        self.cb = None
