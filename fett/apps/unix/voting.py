#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def install (target):
    printAndLog("Installing voting server")
    outLog = ''
    outLog += target.runCommand("mkdir -p /var/www/run")[1]
    outLog += target.runCommand("mkdir -p /var/www/cgi-bin")[1]
    outLog += target.runCommand("mkdir -p /var/www/html")[1]
    outLog += target.runCommand("mkdir -p /var/www/data")[1]

    outLog += target.runCommand("install kfcgi /usr/local/sbin/kfcgi", erroneousContents="install:")[1]
    outLog += target.runCommand("install bvrs /var/www/cgi-bin/bvrs", erroneousContents="install:")[1]
    outLog += target.runCommand("install bvrs.db /var/www/data/bvrs.db", erroneousContents="install:")[1]

    outLog += target.runCommand("echo \"Starting BVRS CGI Handler...\"")[1]

    wwwUser = "www" if isEqSetting('osImage', 'FreeBSD') else "www-data"
    outLog += target.runCommand(f"/usr/local/sbin/kfcgi -s /var/www/run/httpd.sock -U {wwwUser} -u {wwwUser} -p / -- /var/www/cgi-bin/bvrs /var/www/data/bvrs.db")[1]
    return ''

@decorate.debugWrap
@decorate.timeWrap
def deploy (target):
    return ''

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest (target):
    return ''

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest (target):
    return ''
