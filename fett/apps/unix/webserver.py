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
    printAndLog("Installing nginx...")
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

    outLog += target.runCommand("echo \"Starting nginx service...\"")[1]
    if isEqSetting('osImage','debian'):
        outLog += target.runCommand("install nginx.service /lib/systemd/system/nginx.service", erroneousContents="install:")[1]
        outLog += target.runCommand("systemctl start nginx.service", erroneousContents=["Failed to start", "error code"])[1]
    elif isEqSetting('osImage','FreeBSD'):
        outLog += target.runCommand("install -d /usr/local/etc/rc.d")[1]
        outLog += target.runCommand("install rcfile /usr/local/etc/rc.d/nginx", erroneousContents="install:")[1]
        outLog += target.runCommand("service nginx enable", erroneousContents="nginx does not exist")[1]
        outLog += target.runCommand("service nginx start")[1]
    else:
        target.shutdownAndExit (f"Can't start nginx service on <{getSetting('osImage')}>",
                     exitCode=EXIT.Dev_Bug)

    # TODO add errors above

    printAndLog("Nginx installed successfully.")
    return outLog

@decorate.debugWrap
@decorate.timeWrap
def deploy (target):
    # target is a fett target object
    return ''

@decorate.debugWrap
@decorate.timeWrap
def curlTest(target, url, extra=[], http2=False):
    out = curlRequest(url, http2=http2, extra=extra)
    if (not out):
        return (None,None)
    try:
        version,code,*rest = out.splitlines()[0].split(' ')
    except Exception as exc:
        errorAndLog (f"Failed to parse curl output: <{out}>", exc=exc, doPrint=False)
        return (None,None)
    printAndLog(f"curl {url} extra={extra} http2={http2} returned:\n{out}", doPrint=False)
    return (version, code)

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    return deploymentTest(target)

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
    printAndLog("Testing nginx...")
    targetIP = target.ipTarget
    httpPort = target.httpPortTarget
    httpsPort = target.httpsPortTarget
    output = ""

    # 0. Fetch index page
    printAndLog("Test[HTTP]: Fetching index via HTTP", doPrint=False)
    _,code = curlTest(target, f"http://{targetIP}:{httpPort}/index.html")
    if (not code):
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 1. Nginx must be compiled with ssl support
    printAndLog("Test[HTTPS]: Fetching index via HTTPS", doPrint=False)
    _,code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html")
    if (not code):
        target.shutdownAndExit (f"Test[HTTPS]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTPS]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 2. HTTP2 support
    printAndLog("Test[HTTP2]: Fetching index via HTTP2", doPrint=False)
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html", http2=True)
    if (not code):
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Got code {code}].",exitCode=EXIT.Run)
    elif version != 'HTTP/2':
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Got wrong version <{version}>].",exitCode=EXIT.Run)

    # 3. Error redirect is working
    printAndLog("Test[Error Redirect]: Fetching private resource", doPrint=False)
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/private/secret.html")
    if (not code):
        target.shutdownAndExit (f"Test[Error Redirect]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '302':
        target.shutdownAndExit (f"Test[Error Redirect]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 4. "Hidden" resource
    printAndLog("Test[Private Resource]: Fetching private resource from hidden server", doPrint=False)
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/private/secret.html",
                                extra=["-H", "Host: secret_server"])
    if (not code):
        target.shutdownAndExit (f"Test[Private Resource]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[Private Resource]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    printAndLog("Nginx tests OK!")

    return ""
