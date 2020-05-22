#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""
import subprocess

from fett.base.utils.misc import *

@decorate.debugWrap
@decorate.timeWrap
def install (target):
    # target is a fett target object
    appLog = getSetting('appLog')
    printAndLog("Installing nginx...",tee=appLog)
    target.runCommand("echo \"Installing nginx...\"",tee=appLog)
    target.runCommand("mkdir -p /usr/local/sbin",tee=appLog)
    target.runCommand("install nginx /usr/local/sbin/nginx", erroneousContents="install:",tee=appLog)
    target.runCommand("mkdir -p /usr/local/nginx/logs /usr/local/nginx/conf /usr/local/nginx/html",tee=appLog)
    target.runCommand("mkdir -p /usr/local/nginx/post",tee=appLog)
    target.runCommand("mkdir -p /etc/ssl/certs",tee=appLog)
    target.runCommand("mkdir -p /etc/ssl/private",tee=appLog)

    if isEqSetting('osImage','FreeBSD'):
        # The user's name is www on FreeBSD, not www-data:
        target.runCommand("sed -i.bak -e 's/www-data/www/' conf/nginx.conf",tee=appLog)
    target.runCommand("cp -r conf/* /usr/local/nginx/conf/",tee=appLog)
    target.runCommand("cp -r html/* /usr/local/nginx/html/",tee=appLog)
    target.runCommand("cp -r certs/* /etc/ssl/certs",tee=appLog)
    target.runCommand("cp -r keys/* /etc/ssl/private",tee=appLog)

    target.runCommand("echo \"Starting nginx service...\"",tee=appLog)

    if isEqSetting('osImage','debian'):
        target.runCommand("install nginx.service /lib/systemd/system/nginx.service", erroneousContents="install:",tee=appLog)
        target.runCommand("systemctl start nginx.service", erroneousContents=["Failed to start", "error code"],tee=appLog)
    elif isEqSetting('osImage','FreeBSD'):
        target.runCommand("install -d /usr/local/etc/rc.d",tee=appLog)
        target.runCommand("install rcfile /usr/local/etc/rc.d/nginx", erroneousContents="install:",tee=appLog)
        target.runCommand("service nginx enable", erroneousContents="nginx does not exist",tee=appLog)
        target.runCommand("service nginx start", erroneousContents=["failed"], tee=appLog)
    else:
        target.shutdownAndExit (f"Can't start nginx service on <{getSetting('osImage')}>",
                     exitCode=EXIT.Dev_Bug)

    printAndLog("Nginx installed successfully.",tee=appLog)
    return

@decorate.debugWrap
@decorate.timeWrap
def deploy (target):
    printAndLog ("Deployment successful. Target is ready.",tee=getSetting('appLog'))
    
    #Here we should send a message to the portal

    #Here we should wait for a termination signal from the portal
    
    printAndLog("Termination signal received. Preparing to exit...",tee=getSetting('appLog'))
    return

@decorate.debugWrap
@decorate.timeWrap
def curlTest(target, url, extra=[], http2=False):
    out = curlRequest(url, http2=http2, extra=extra, rawOutput=False)
    if (not out):
        return (None,None)
    try:
        version,code,*rest = out.splitlines()[0].split(' ')
    except Exception as exc:
        errorAndLog (f"Failed to parse curl output: <{out}>", exc=exc, doPrint=False)
        return (None,None)
    printAndLog(f"curl {url} extra={extra} http2={http2} returned:\n{out}", doPrint=False,tee=getSetting('appLog'))
    return (version, code)

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    deploymentTest(target)

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    """
    Let's make sure that the deployed web app is working correctly by issuing
    some basic requests.

    The web app is supposed to expose the features that were listed as
    requirements for the web server, so design/nginix_requirements.lando is the
    guidance as to what tests we should run here.

    """
    printAndLog("Testing nginx...",tee=getSetting('appLog'))
    targetIP = target.ipTarget
    httpPort = target.httpPortTarget
    httpsPort = target.httpsPortTarget

    # 0. Fetch index page
    printAndLog("Test[HTTP]: Fetching index via HTTP", doPrint=False,tee=getSetting('appLog'))
    _,code = curlTest(target, f"http://{targetIP}:{httpPort}/index.html")
    if (not code):
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 1. Nginx must be compiled with ssl support
    printAndLog("Test[HTTPS]: Fetching index via HTTPS", doPrint=False,tee=getSetting('appLog'))
    _,code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html")
    if (not code):
        target.shutdownAndExit (f"Test[HTTPS]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTPS]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 2. HTTP2 support
    printAndLog("Test[HTTP2]: Fetching index via HTTP2", doPrint=False,tee=getSetting('appLog'))
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html", http2=True)
    if (not code):
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Got code {code}].",exitCode=EXIT.Run)
    elif version != 'HTTP/2':
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Got wrong version <{version}>].",exitCode=EXIT.Run)

    # 3. Error redirect is working
    printAndLog("Test[Error Redirect]: Fetching private resource", doPrint=False,tee=getSetting('appLog'))
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/private/secret.html")
    if (not code):
        target.shutdownAndExit (f"Test[Error Redirect]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '302':
        target.shutdownAndExit (f"Test[Error Redirect]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 4. "Hidden" resource
    printAndLog("Test[Private Resource]: Fetching private resource from hidden server", doPrint=False,tee=getSetting('appLog'))
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/private/secret.html",
                                extra=["-H", "Host: secret_server"])
    if (not code):
        target.shutdownAndExit (f"Test[Private Resource]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[Private Resource]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    printAndLog("Nginx tests OK!",tee=getSetting('appLog'))

    return
