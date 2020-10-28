# Adapted from the program_flash sh script from the GFE repository
# url: git@gitlab-ext.galois.com:ssith/gfe.git
# revision: e1b3a1463e1ffe2ef2c020c8982f72ab80e2392c

#vivado_lab -source ./prog_flash.tcl -log \
./prog_flash.log -mode batch -tclargs localhost:3121/xilinx_tcf/Digilent/210308A5F7BB ./small.bin

if { [llength $argv] != 2 } {
    puts "ERROR!! Did not pass proper number of arguments to this script."
    puts "args: <target name> <bin file>"
    exit -1
}

set hwtarget [lindex $argv 0]
set binfile [lindex $argv 1]

set hwId [lindex [split $hwtarget '/'] end]
set tmpfile "./flash_${hwId}.mcs"

# Create file for programming flash memory.
write_cfgmem -force -format MCS -size 128 -interface SPIx8 -loaddata "up 0x04000000 ${binfile}" ${tmpfile}
set files [list "./flash_${hwId}_primary.mcs" "./flash_${hwId}_secondary.mcs" ]

set_param xicom.use_bitstream_version_check false
open_hw
connect_hw_server
current_hw_target $hwtarget
set_property PARAM.FREQUENCY 15000000 [current_hw_target]
open_hw_target
current_hw_device [get_hw_devices xcvu9p_0]
refresh_hw_device -update_hw_probes false [current_hw_device]
create_hw_cfgmem -hw_device [current_hw_device] [lindex [get_cfgmem_parts {mt25qu01g-spi-x1_x2_x4_x8}] 0]

set_property -dict [ list \
             PROGRAM.ADDRESS_RANGE {use_file} \
             PROGRAM.FILES $files \
             PROGRAM.UNUSED_PIN_TERMINATION {pull-none} \
             PROGRAM.BLANK_CHECK 0 \
             PROGRAM.ERASE 1 \
             PROGRAM.CFG_PROGRAM 1 \
             PROGRAM.VERIFY 1 \
             PROGRAM.CHECKSUM 0 \
            ] [current_hw_cfgmem]

program_hw_cfgmem

close_hw_target
disconnect_hw_server
close_hw
puts "Done!"
exit 0