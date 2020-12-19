#!/bin/sh

# PROVIDE: ota
# REQUIRE: DAEMON
# KEYWORD: shutdown

. /etc/rc.subr

name="ota"
desc="OTA Update Server"
rcvar="ota_enable"

command="/usr/local/sbin/${name}"
command_args="/root/key &"

pidfile="/var/run/${name}.pid"

load_rc_config $name
: ${ota_enable:="no"}

run_rc_command "$1"
