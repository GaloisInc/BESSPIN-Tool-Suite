#!/bin/sh

# PROVIDE: nginx
# REQUIRE: DAEMON
# KEYWORD: shutdown

. /etc/rc.subr

name=nginx
rcvar=nginx_enable
command=/usr/local/sbin/nginx

load_rc_config $name
: ${nginx_enable:=no}
: ${nginx_prefix=/usr/local/nginx}

command_args="-p ${nginx_prefix}"
pidfile=${nginx_prefix}/logs/nginx.pid

run_rc_command "$1"
