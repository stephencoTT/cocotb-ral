####### WIP #########

# cocotb-ral
Repo for the cocotb-ral library and follows the KISS model (Keep It Stupidly Simple)

# Objective
Many design verification engineers have come from and/or experienced SV-UVM during their career and thus are familiar with UVM RAL.  cocotb does not implement a RAL (as of this writing), thus setting up registers for hardware access is cumbersome.  Depending on who you talk to and which company you work with, cocotb RAL implementations can vary widely.

This library aims to provide straightforward access methods that most of us have come to use (and love):
- write_reg(addr, data)
- read_reg(addr, data)
- write_reg_field(addr, data)
- read_reg_field(addr, data)

That's it, we don't need anything else.  The above will cover 99% of scenarios.

The general steps to use this are:
1. Create an interface driver using the reg_driver class.  You can create as many as you want, but generally you just want 1 per register interface
2. Create the RAL class constructs from an RDL input file and assign it to the driver.  If you don't have an RDL file, then look further below for a basic spec on how we put them together.  Also, tell your designers to create an RDL for their design please like come on.
3. The driver now has capability to use the above 4 read/write methods to address registers and fields by their string names.  If you try to use them without assigning the RAL class, it will throw an error.
4. The class has some built-in checking.
5. Reset value checking, on the very first read, check that the readback value matches the reset value), applies for all fields except for WO and W1C and field must be non-volatile
6. RAW checking (read-after-write), reads to fields must return the last written value (or reset value) if the field is R/W and field must be non-volatile
The RAL essentially keeps a mirror (shadow) copy of the registers where the starting value is the reset value.  I don't intend to implement the mirroring methods like in the UVM classes, its a bit overkill for now.  Maybe if demand warrants it...

Other reg attributes aren't supported yet because honestly no one really uses it unless they are a maniac (W0C, R1C, R0C).

# Usage
import reg_driver from cocotb-ral
import rdl2ral from cocotb-ral

apb_driver = reg_driver() # instance of interface driver
apb_driver.protocol = AXI3 # APB3/APB4/AXI4, regardless of protocol, will use default 32-bit data width and 64-bit addressing, can be reconfigured.
apb_driver.data_width = 32
apb_driver.addr_width = 32
apb_driver.ral = rdl2ral('blah.rdl') # Take an RDL file, and create a special python RAL class out of which defines registers

apb_driver.write('DUT.REG1', data)
apb_driver.read('DUT.REG2', rdata)

# RAL register template
class REGISTERNAME:
  addr = 0xDEADBEEF
  f = {
        FIELD0, 0, 4, RO,
        FIELD1, 5, RO,
        FIELD2, 6-15, RW,
        FIELD3, 16-31, RW
      }
