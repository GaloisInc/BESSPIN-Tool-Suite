#!/bin/sh

# PROVIDE: bvrs
# REQUIRE: nginx
# KEYWORD: shutdown

. /etc/rc.subr

name="bvrs"
desc="Voter registration system for FETT"
rcvar="bvrs_enable"

procname="/usr/local/sbin/kfcgi"
command="/usr/sbin/daemon"
bvrs_prog="/var/www/cgi-bin/bvrs"
pidfile="/var/run/bvrs.pid"

dbfile="/var/www/data/bvrs.db"

load_rc_config $name
: ${bvrs_enable:="no"}
: ${bvrs_flags:="-s /var/www/run/httpd.sock -U www -u www -p /"}

# run_rc_command would send ${name}_flags as parameters to $command (daemon).
# This ensures they are actually passed to kfcgi instead.
actual_bvrs_flags="${bvrs_flags}"
bvrs_flags=""
command_args="-f -p ${pidfile} -- ${procname} -d ${actual_bvrs_flags} -- ${bvrs_prog} ${dbfile}"

run_rc_command "$1"
