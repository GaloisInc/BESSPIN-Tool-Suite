#!/bin/sh

# PROVIDE: infotainment-server
# REQUIRE: DAEMON
# KEYWORD: shutdown

. /etc/rc.subr

name="infotainment_server"
desc="Infotainment Server"
rcvar="infotainment_server_enable"

command="/usr/local/sbin/${name}"

pidfile="/var/run/${name}.pid"

load_rc_config $name
: ${infotainment_server_enable:="no"}

run_rc_command "$1"
