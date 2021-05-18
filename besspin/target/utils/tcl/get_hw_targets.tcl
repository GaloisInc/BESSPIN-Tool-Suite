# Get a list of all available hw_targets

open_hw
connect_hw_server
set listTargets [get_hw_targets]
puts "listTargets=<$listTargets>"
disconnect_hw_server
close_hw
exit 0
