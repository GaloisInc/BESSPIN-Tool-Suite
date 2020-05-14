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

    # TODO add errors above

    printAndLog("Nginx installed successfully.")
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

def curlTest(target, url, extra=[], http2=False):
    out = curlRequest(url, http2=http2, extra=extra)
    try:
        version,code,*rest = out.splitlines()[0].split(' ')
    except Exception as exc:
        logAndExit(f"Failed to parse curl output: <{out}>", exc=exc, exitCode=EXIT.Run)
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
    try:
        _,code = curlTest(target, f"http://{targetIP}:{httpPort}/index.html")
        if code != '200':
            logAndExit(f"Failed to fetch index via HTTP, got code {code}")
    except Exception as exc:
        logAndExit("Failed to fetch index via HTTP", exc=exc)

    # 1. Nginx must be compiled with ssl support
    printAndLog("Test[HTTPS]: Fetching index via HTTPS", doPrint=False)
    try:
        _,code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html")
        if code != '200':
            logAndExit(f"Failed to fetch index via HTTPS, got code {code}")
    except Exception as exc:
        logAndExit("Failed to fetch index via HTTPS", exc=exc)

    # 2. HTTP2 support
    printAndLog("Test[HTTP2]: Fetching index via HTTP2", doPrint=False)
    try:
        version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html", http2=True)
        if code != '200':
            logAndExit(f"Failed to fetch index via HTTP/2, got code {code}")
        if version != 'HTTP/2':
            logAndExit(f"Failed to fetch index via HTTP/2, got wrong version <{version}>")
    except Exception as exc:
        logAndExit("Failed to fetch index via HTTPS", exc=exc)

    # 3. Error redirect is working
    printAndLog("Test[Error Redirect]: Fetching private resource", doPrint=False)
    try:
        version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/private/secret.html")
        if code != '302':
            logAndExit(f"No redirect after attempt to fetch private resource, got code {code}")
    except Exception as exc:
        logAndExit("Failed to test error redirection", exc=exc)

    # 4. "Hidden" resource
    printAndLog("Test[Error Redirect]: Fetching private resource", doPrint=False)
    try:
        version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/private/secret.html",
                                extra=["-H", "Host: secret_server"])
        if code != '200':
            logAndExit(f"Could not fetch resource from hidden server, got code {code}")
    except Exception as exc:
        logAndExit("Failed to test error redirection", exc=exc)

    printAndLog("Nginx tests OK!")

    return ""
