import cocotb
from cocotb.handle import Force, Release
from cocotb.triggers import RisingEdge, Timer

# (Include the register definitions, RAL, and APBDriver classes here as well)

# Dictionary to hold your register definitions for the RAL
register_definitions = {
    "SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE": {
        "class": SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_reg_u,
        "offset": SMN_SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_OFFSET,
        "addr": SMN_SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_ADDR
    },
    # Add other registers here
}


@cocotb.test()
async def ral_test_translator_api(dut):
    """Test the RAL layer with translator methods."""

    cocotb.log.info("Starting RAL test with translator methods")

    apb_driver_i = APBDriver(dut)
    ral = RAL(register_definitions)
    ral.connect(apb_driver_i)

    # --- Write using hierarchical path ---
    cocotb.log.info("--- Writing via hierarchical path ---")
    write_data_1 = 0x1A2B3C4D
    status_write_1 = {"success": False, "error": None} # Initialize status dict
    await ral.write(
        "SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE",
        write_data_1,
        status_write_1
    )
    if status_write_1["success"]:
        cocotb.log.info(f"Write successful to SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE with data 0x{write_data_1:08x}")
    else:
        cocotb.log.error(f"Write failed: {status_write_1['error']}")

    # Verify internal RAL model update
    internal_val = ral.SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE.val
    cocotb.log.info(f"Internal RAL model value after write: 0x{internal_val:08x}")
    assert internal_val == write_data_1, "Internal RAL model not updated correctly after write"


    # --- Read using hierarchical path ---
    cocotb.log.info("--- Reading via hierarchical path ---")
    read_data_1 = {"value": 0} # Initialize read_data dict
    status_read_1 = {"success": False, "error": None} # Initialize status dict
    await ral.read(
        "SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE",
        read_data_1,
        status_read_1
    )
    if status_read_1["success"]:
        cocotb.log.info(f"Read successful from SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE: 0x{read_data_1['value']:08x}")
    else:
        cocotb.log.error(f"Read failed: {status_read_1['error']}")

    # Verify that the read value matches the simulated value from the driver
    expected_read_val = 0xDEADBEEFC0FFEE # Based on APBDriver's simulated read
    assert read_data_1['value'] == expected_read_val, \
        f"Read data mismatch: Expected 0x{expected_read_val:x}, got 0x{read_data_1['value']:x}"


    # --- Write using numerical address (full address) ---
    cocotb.log.info("--- Writing via numerical full address ---")
    write_data_2 = 0xAABBCCDD
    status_write_2 = {"success": False, "error": None}
    await ral.write(
        SMN_SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_ADDR,
        write_data_2,
        status_write_2
    )
    if status_write_2["success"]:
        cocotb.log.info(f"Write successful to 0x{SMN_SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_ADDR:08x} with data 0x{write_data_2:08x}")
    else:
        cocotb.log.error(f"Write failed: {status_write_2['error']}")

    # --- Read using numerical address (offset) ---
    cocotb.log.info("--- Reading via numerical offset address ---")
    read_data_2 = {"value": 0}
    status_read_2 = {"success": False, "error": None}
    await ral.read(
        SMN_SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_OFFSET,
        read_data_2,
        status_read_2
    )
    if status_read_2["success"]:
        cocotb.log.info(f"Read successful from 0x{SMN_SMN_MST_COMMON_BLOCK_SMN_MST_INT_ENABLE_REG_OFFSET:08x}: 0x{read_data_2['value']:08x}")
    else:
        cocotb.log.error(f"Read failed: {status_read_2['error']}")

    # Test error handling: non-existent address
    cocotb.log.info("--- Testing non-existent address read ---")
    read_data_invalid = {"value": 0}
    status_invalid = {"success": False, "error": None}
    await ral.read(0xFFFFFFFF, read_data_invalid, status_invalid) # A non-existent address
    if not status_invalid["success"]:
        cocotb.log.info(f"Caught expected error for non-existent address: {status_invalid['error']}")
    else:
        cocotb.log.error("Did not catch expected error for non-existent address.")

    cocotb.log.info("RAL test with translator methods finished")