# Initial script from the GFE repository
# url: git@gitlab-ext.galois.com:ssith/gfe.git
# revision: e1b3a1463e1ffe2ef2c020c8982f72ab80e2392c

if { [llength $argv] != 3 } {
    puts "ERROR!! Did not pass proper number of arguments to this script."
    puts "args: <target name> <bitfile path> <ltxfile path>"
    exit -1
}
set hwtarget [lindex $argv 0]
set bitfile [lindex $argv 1]
set probfile [lindex $argv 2]

open_hw
connect_hw_server
current_hw_target $hwtarget
open_hw_target
current_hw_device [get_hw_devices xcvu9p_0]
# refresh_hw_device -update_hw_probes false [lindex [get_hw_devices xcvu9p_0] 0]
set_property PROBES.FILE $probfile [get_hw_devices xcvu9p_0]
set_property FULL_PROBES.FILE $probfile [get_hw_devices xcvu9p_0]
set_property PROGRAM.FILE $bitfile [get_hw_devices xcvu9p_0]
puts "---------------------"
puts "Program Configuration"
puts "---------------------"
puts "hw_target: $hwtarget"
puts "Bitstream : $bitfile"
puts "Probe Info: $probfile"
puts ""
puts "Programming..."
program_hw_devices [get_hw_devices xcvu9p_0]
close_hw_target
disconnect_hw_server
close_hw
puts "Done!"
exit 0
