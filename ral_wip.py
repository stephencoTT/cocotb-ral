import cocotb
from cocotb.handle import Force, Release
from cocotb.triggers import RisingEdge, Timer
from ctypes import Structure, Union, c_uint32, c_uint64

# Assume your register definitions are in a file named 'registers.py'

# For this example, I'll include the one you provided

# registers.py (start)

SMN_SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_OFFSET = 0x00000098
SMN_SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_ADDR = 0x10000003010098

class SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_reg_t(Structure):
    _fields_ = [
        ('smn_network_err', c_uint32, 1),
        ('cmd_timeout', c_uint32, 1),
        ('resp_timeout', c_uint32, 1),
        ('resp_err', c_uint32, 1),
        ('resp_frame', c_uint32, 1),
        ('token_timeout', c_uint32, 1),
        ('token_request', c_uint32, 1),
        ('cmd_desc_rdy', c_uint32, 1),
        ('cmd_data_rdy', c_uint32, 1),
    ]

SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_DEFAULT = 0x00000000

class SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_reg_u(Union):
    _fields_ = [
        ('val', c_uint64), # Changed to c_uint64 to match addr, assuming 64-bit access
        ('f', SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_reg_t),
    ]

    def __init__(self, *args, **kwargs):
        super(SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_reg_u, self).__init__(*args, **kwargs)
        self.val = SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_DEFAULT

    def as_bytes(self):
        # Determine the size of 'val' based on its type
        size = 4 if isinstance(self.val, c_uint32) else 8 # Adjusted logic based on c_uint64
        return self.val.to_bytes(size, 'little')

    @classmethod
    def from_bytes(cls, byte_seq):
        instance = cls()
        instance.val = int.from_bytes(byte_seq, 'little')
        return instance

# registers.py (end)

class RAL:
    def __init__(self, register_definitions):
        self._registers = {}
        self._address_map = {}

        for reg_name, reg_info in register_definitions.items():
            reg_class = reg_info['class']
            reg_addr = reg_info['addr']
            reg_offset = reg_info['offset']

            # Instantiate the register union
            reg_instance = reg_class()
            setattr(self, reg_name, reg_instance) # Allows access like ral.SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE
            self._registers[reg_name] = reg_instance
            self._address_map[reg_addr] = reg_instance
            self._address_map[reg_offset] = reg_instance # Map offset as well for flexibility

    async def _perform_transaction(self, driver, addr, data_bytes, is_write):
        """Helper to perform the actual APB transaction."""
        status = {"success": False}
        if is_write:
            await driver.write(addr, data_bytes, status)
        else:
            await driver.read(addr, data_bytes, status)
        return status

    async def read(self, register_identifier):
        """
        Reads a register from the hardware.

        Args:
            register_identifier: Can be a numerical address (int) or a string
                                 representing the hierarchical register path.

        Returns:
            A tuple (data_value, status_dict) where data_value is the integer
            value read from the register and status_dict indicates success/failure.
        """
        reg_instance = None
        addr = None
        if isinstance(register_identifier, int):
            addr = register_identifier
            reg_instance = self._address_map.get(addr)
            if not reg_instance:
                cocotb.log.error(f"Address 0x{addr:08x} not found in RAL address map.")
                return 0, {"success": False, "error": "Address not found"}
        elif isinstance(register_identifier, str):
            reg_instance = getattr(self, register_identifier, None)
            if not reg_instance:
                cocotb.log.error(f"Register '{register_identifier}' not found in RAL.")
                return 0, {"success": False, "error": "Register not found"}
            # Find the address associated with this register instance
            for a, r in self._address_map.items():
                if r is reg_instance:
                    addr = a
                    break
            if addr is None:
                cocotb.log.error(f"Could not find address for register '{register_identifier}'.")
                return 0, {"success": False, "error": "Address not found"}
        else:
            cocotb.log.error("Invalid register identifier type. Must be int or str.")
            return 0, {"success": False, "error": "Invalid identifier type"}

        # Determine the size of the register (assuming from the 'val' field of the Union)
        # This assumes the 'val' field is always present and determines the access size.
        size_bytes = 8 # Default to 64-bit
        if hasattr(reg_instance, 'val') and isinstance(reg_instance.val, c_uint32):
             size_bytes = 4

        read_data_bytes = bytearray(size_bytes) # Prepare a bytearray to receive data
        status = await self._perform_transaction(self._driver, addr, read_data_bytes, is_write=False)

        if status["success"]:
            # Update the internal register model with the read value
            reg_instance.val = int.from_bytes(read_data_bytes, 'little')
            return reg_instance.val, status
        else:
            return 0, status

    async def write(self, register_identifier, data):
        """
        Writes data to a register in the hardware.

        Args:
            register_identifier: Can be a numerical address (int) or a string
                                 representing the hierarchical register path.
            data: The integer value to write.

        Returns:
            A status dictionary indicating success/failure.
        """
        reg_instance = None
        addr = None
        if isinstance(register_identifier, int):
            addr = register_identifier
            reg_instance = self._address_map.get(addr)
            if not reg_instance:
                cocotb.log.error(f"Address 0x{addr:08x} not found in RAL address map.")
                return {"success": False, "error": "Address not found"}
        elif isinstance(register_identifier, str):
            reg_instance = getattr(self, register_identifier, None)
            if not reg_instance:
                cocotb.log.error(f"Register '{register_identifier}' not found in RAL.")
                return {"success": False, "error": "Register not found"}
            # Find the address associated with this register instance
            for a, r in self._address_map.items():
                if r is reg_instance:
                    addr = a
                    break
            if addr is None:
                cocotb.log.error(f"Could not find address for register '{register_identifier}'.")
                return {"success": False, "error": "Address not found"}
        else:
            cocotb.log.error("Invalid register identifier type. Must be int or str.")
            return {"success": False, "error": "Invalid identifier type"}

        # Update the internal register model with the value to be written
        reg_instance.val = data
        data_bytes = reg_instance.as_bytes()

        status = await self._perform_transaction(self._driver, addr, data_bytes, is_write=True)
        return status

    def connect(self, driver):
        """Connects the RAL to the APB driver."""
        self._driver = driver
        driver.ral = self # Allow driver to access RAL if needed (e.g., for callbacks)
