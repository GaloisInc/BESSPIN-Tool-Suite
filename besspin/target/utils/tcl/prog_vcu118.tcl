# Should be called as follows:
# vivado_lab -source ./prog_vcu118.tcl -log ./prog_vcu118.log\
 -mode batch -tclargs <bitstreamAndData_flash|bitstream_nonpersistent> <target name> <bitstream> <binary file|probe file>

proc usageAndExit {} {
    puts "prog_vcu118.tcl (program the VCU118 utility)"
    puts "arguments:"
    puts "\toption          {bitstreamAndData_flash,bitstream_nonpersistent}"
    puts "\ttarget name     (example: localhost:3121/xilinx_tcf/Digilent/210308A5F7BB)"
    puts "\tbitstream         The path to the bitstream"
    puts "\t<binary|probe file     The path to either the binary file (if option is flash) or the ltx file (if option is nonpersistent)"
    exit -1
}

# Manually arse input arguments and interpret them
if { [llength $argv] != 4 } {
    puts "ERROR! Did not pass proper number of arguments to this script."
    usageAndExit
}

set option [lindex $argv 0]
if { ![string equal $option "bitstreamAndData_flash"] && ![string equal $option "bitstream_nonpersistent"] } {
    puts "ERROR! Invalid option <$option>."
    usageAndExit
}

set hwtarget [lindex $argv 1]
set hwId [lindex [split $hwtarget '/'] end]

set bitstream [lindex $argv 2]

if { [string equal "$option" "bitstreamAndData_flash"] } {
    set binfile [lindex $argv 3]
} else {
    set probefile [lindex $argv 3]   
}


# Create config files needed to program the flash
if { [string equal "$option" "bitstreamAndData_flash"] } {
    set flashBitfilePrefix "./flash_bitfile_${hwId}"
    set flashDatafilePrefix "./flash_datafile_${hwId}"
    # bitstream max is <50M and binfile max is <100M
    # Regarding the starting point for loaddata (0x04000000), 64M > 50M so it's a reasonable choice too
    # If the sizes are smaller, vivado will adjust them accordingly
    
    write_cfgmem -force -verbose -format MCS -size 64 -interface SPIx8 \
        -loadbit "up 0x00000000 ${bitstream}" \
        "${flashBitfilePrefix}.mcs"
    write_cfgmem -force -verbose -format MCS -size 128 -interface SPIx4 \
        -loaddata "up 0x04000000 ${binfile}" \
        "${flashDatafilePrefix}.mcs"
    set flashBitfileMcsFiles [list "${flashBitfilePrefix}_primary.mcs" "./${flashBitfilePrefix}_secondary.mcs" ]
    set flashBitfilePrmFiles [list "./${flashBitfilePrefix}_primary.prm" "./${flashBitfilePrefix}_secondary.prm" ]
    set flashDatafileMcsFiles [list "${flashDatafilePrefix}.mcs" ] 
    set flashDatafilePrmFiles [list "./${flashDatafilePrefix}.prm" ] 
}

# Connect to the board and sets the correct hwId
#set_param xicom.use_bitstream_version_check false
open_hw
connect_hw_server
current_hw_target $hwtarget
#set_property PARAM.FREQUENCY 15000000 [current_hw_target]
open_hw_target -verbose
current_hw_device [get_hw_devices xcvu9p_0]

# Need to create a cfgmem associated with the hw_device
create_hw_cfgmem -verbose -hw_device [current_hw_device] [lindex [get_cfgmem_parts {mt25qu01g-spi-x1_x2_x4_x8}] 0]

# For flash, we do the following:
# 1. Set the properties needed for programming the bitstream
# 2. Program the flash with bitstream
# 3. Set the properties needed for programming the datafile
# 4. Program the flash with datafile
if { [string equal "$option" "bitstreamAndData_flash"] } {
    #Step 1
    set_property -dict [ list \
        PROGRAM.ADDRESS_RANGE {entire_device} \
        PROGRAM.FILES $flashBitfileMcsFiles \
        PROGRAM.PRM_FILES $flashBitfilePrmFiles \
        PROGRAM.UNUSED_PIN_TERMINATION {pull-none} \
        PROGRAM.BLANK_CHECK 0 \
        PROGRAM.ERASE 1 \
        PROGRAM.CFG_PROGRAM 1 \
        PROGRAM.VERIFY 1 \
        PROGRAM.CHECKSUM 0 \
    ] [current_hw_cfgmem]
    #Step 2
    program_hw_devices -verbose
    refresh_hw_device -verbose -update_hw_probes false [current_hw_device]
    program_hw_cfgmem -verbose

    #Step 3
    set_property -dict [ list \
        PROGRAM.ADDRESS_RANGE {use_file} \
        PROGRAM.FILES $flashDatafileMcsFiles \
        PROGRAM.PRM_FILES $flashDatafilePrmFiles \
        PROGRAM.UNUSED_PIN_TERMINATION {pull-none} \
        PROGRAM.BLANK_CHECK 0 \
        PROGRAM.ERASE 0 \
        PROGRAM.CFG_PROGRAM 1 \
        PROGRAM.VERIFY 1 \
        PROGRAM.CHECKSUM 0 \
    ] [current_hw_cfgmem]
    #Step 4
    program_hw_cfgmem -verbose
}


# For bit, we do the following:
# 1. Set the properties needed for erasing the hw_cfgmem
# 2. Empty hw_device and erase the flash contents
# 3. Program the hw_device
if { [string equal "$option" "bitstream_nonpersistent"] } {
    #Step 1
    set_property -dict [ list \
        PROGRAM.ADDRESS_RANGE {entire_device} \
        PROGRAM.UNUSED_PIN_TERMINATION {pull-none} \
        PROGRAM.FILES "" \
        PROGRAM.PRM_FILES "" \
        PROGRAM.BLANK_CHECK 0 \
        PROGRAM.ERASE 1 \
        PROGRAM.CFG_PROGRAM 0 \
        PROGRAM.VERIFY 0 \
        PROGRAM.CHECKSUM 0
    ] [current_hw_cfgmem]
    #Step 2
    program_hw_devices -verbose
    refresh_hw_device -verbose -update_hw_probes false [current_hw_device]
    program_hw_cfgmem -verbose 
    #Step 3
    set_property -dict [ list \
        PROBES.FILE $probefile \
        FULL_PROBES.FILE $probefile \
        PROGRAM.FILE $bitstream
    ] [current_hw_device]
    program_hw_devices -verbose
}

# Close and disconnect
close_hw_target
disconnect_hw_server
close_hw
puts "Done!"
exit 0
