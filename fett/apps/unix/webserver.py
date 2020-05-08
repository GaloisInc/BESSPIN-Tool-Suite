#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def install (target):
    # target is a fett target object
    outLog = ''
    outLog += target.runCommand("echo \"Installing nginx...\"")[1]
    outLog += target.runCommand("mkdir -p /usr/local/sbin")[1]
    outLog += target.runCommand("install nginx /usr/local/sbin/nginx", erroneousContents="install:")[1]
    outLog += target.runCommand("mkdir -p /usr/local/nginx/logs /usr/local/nginx/conf /usr/local/nginx/html")[1]
    outLog += target.runCommand("mkdir -p /usr/local/nginx/post")[1]
    outLog += target.runCommand("mkdir -p /etc/ssl/certs")[1]
    outLog += target.runCommand("mkdir -p /etc/ssl/private")[1]

    outLog += target.runCommand("cp -r conf/* /usr/local/nginx/conf/")[1]
    outLog += target.runCommand("cp -r html/* /usr/local/nginx/html/")[1]
    outLog += target.runCommand("cp -r certs/* /etc/ssl/certs")[1]
    outLog += target.runCommand("cp -r keys/* /etc/ssl/private")[1]

    # TODO add errors above
    return outLog

@decorate.debugWrap
@decorate.timeWrap
def deploy (target):
    # target is a fett target object
    outLog = ''
    outLog += target.runCommand("echo \"Starting nginx service...\"")[1]
    if getSetting('osImage') == 'debian':
        outLog += target.runCommand("install nginx.service /lib/systemd/system/nginx.service", erroneousContents="install:")[1]
        outLog += target.runCommand("systemctl start nginx.service", erroneousContents=["Failed to start", "error code"])[1]
    elif getSetting('osImage') == 'FreeBSD':
        outLog += target.runCommand("install -d /usr/local/etc/rc.d")[1]
        outLog += target.runCommand("install rcfile /usr/local/etc/rc.d/nginx", erroneousContents="install:")[1]
        outLog += target.runCommand("service nginx enable", erroneousContents="nginx does not exist")[1]
        outLog += target.runCommand("service nginx start")[1]
    else:
        logAndExit (f"Can't start nginx service on <{getSetting('osImage')}>",
                     exitCode=EXIT.Configuration)
    return outLog
