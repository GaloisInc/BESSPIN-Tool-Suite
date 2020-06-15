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
def curlTest(target, url, extra=[], http2=False, method="GET", rawOutput=False):
    out = curlRequest(url, http2=http2, extra=extra, method=method, rawOutput=rawOutput)
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
def dumpLogs(target):
    appLog = getSetting('appLog')
    webserverDir = os.path.join(getSetting('workDir'),'webserver')
    printAndLog(f"Dumping webserver logs to {webserverDir}...", tee=getSetting('appLog'))
    mkdir(webserverDir)
    weblogs = getSetting("webserverLogs")
    root    = weblogs["root"]
    user    = target.userName
    userRoot = os.path.join("/", "{user}", "{root}")

    target.runCommand(f"mkdir -p {userRoot}", shutdownOnError=False, tee=appLog)
    for l in weblogs["logs"]:
        target.runCommand(f"chown -f {userRoot}/{l}", shutdownOnError=False, tee=appLog)
        target.runCommand(f"mkdir -p {userRoot}")
        target.runCommand(f"cp {root}/{l} {userRoot}/{l}", shutdownOnError=False, tee=appLog)

    if target.isCurrentUserRoot:
        target.switchUser()
    if not target.isSshConn:
        if not target.openSshConn(userName=target.userName,timeout=30):
            printAndLog("Failed to open an SSH connection to the target, resorting to console")

    # These are the standard nginx logs
    for l in weblogs["logs"]:
        localLogName = os.path.join(webserverDir, l)
        log = ftOpenFile(localLogName, 'w')
        target.sendFile(localLogName, l, toTarget=False, targetPath=userRoot, shutdownOnError=False)
        log.close()
        printAndLog(f"Grabbed webserver log <{l}>")

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
    target.genStdinEntropy()
    printAndLog("Test[HTTP]: Fetching index via HTTP", doPrint=False,tee=getSetting('appLog'))
    _,code = curlTest(target, f"http://{targetIP}:{httpPort}/index.html")
    if (not code):
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 1. Nginx must be compiled with ssl support
    target.genStdinEntropy()
    printAndLog("Test[HTTPS]: Fetching index via HTTPS", doPrint=False,tee=getSetting('appLog'))
    _,code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html")
    if (not code):
        target.shutdownAndExit (f"Test[HTTPS]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTPS]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 2. HTTP2 support
    target.genStdinEntropy()
    printAndLog("Test[HTTP2]: Fetching index via HTTP2", doPrint=False,tee=getSetting('appLog'))
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html", http2=True)
    if (not code):
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Got code {code}].",exitCode=EXIT.Run)
    elif version != 'HTTP/2':
        target.shutdownAndExit (f"Test[HTTP2]: Failed! [Got wrong version <{version}>].",exitCode=EXIT.Run)

    # 3. Error redirect is working
    target.genStdinEntropy()
    printAndLog("Test[Error Redirect]: Fetching private resource", doPrint=False,tee=getSetting('appLog'))
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/private/secret.html")
    if (not code):
        target.shutdownAndExit (f"Test[Error Redirect]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '302':
        target.shutdownAndExit (f"Test[Error Redirect]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 4. "Hidden" resource
    target.genStdinEntropy()
    printAndLog("Test[Private Resource]: Fetching private resource from hidden server", doPrint=False,tee=getSetting('appLog'))
    version,code = curlTest(target, f"https://{targetIP}:{httpsPort}/private/secret.html",
                                extra=["-H", "Host: secret_server"])
    if (not code):
        target.shutdownAndExit (f"Test[Private Resource]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit (f"Test[Private Resource]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # 5. Fetching text.txt via HTTP
    target.genStdinEntropy()
    printAndLog("Test[Text File]: Fetching text.txt via HTTP", doPrint=False, tee=getSetting('appLog'))
    _, code = curlTest(target, f"http://{targetIP}:{httpPort}/test.txt")
    if (not code):
        target.shutdownAndExit(f"Test[Text File]: Failed! [Fatal]", exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit(f"Test[Text File]: Failed! [Got code {code}].", exitCode=EXIT.Run)

    # 6. Fetching static.html  via HTTP
    target.genStdinEntropy()
    printAndLog("Test[Static HTTP]: Fetching static.html via HTTP", doPrint=False, tee=getSetting('appLog'))
    _, code = curlTest(target, f"http://{targetIP}:{httpPort}/static.html")
    if (not code):
        target.shutdownAndExit(f"Test[Static HTTP]: Failed! [Fatal]", exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit(f"Test[Static HTTP]: Failed! [Got code {code}].", exitCode=EXIT.Run)

    # 7. Fetching stanford.png - an image via HTTP
    target.genStdinEntropy()
    printAndLog("Test[Image Resource]: Fetching stanford.png via HTTP", doPrint=False, tee=getSetting('appLog'))
    _, code = curlTest(target, f"http://{targetIP}:{httpPort}/stanford.png")
    if (not code):
        target.shutdownAndExit(f"Test[Image Resource]: Failed! [Fatal]", exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit(f"Test[Image Resource]: Failed! [Got code {code}].", exitCode=EXIT.Run)

    # 8. Fetching static https web page
    target.genStdinEntropy()
    printAndLog("Test[Static HTTP2]: Fetching static https web page", doPrint=False, tee=getSetting('appLog'))
    version, code = curlTest(target, f"https://{targetIP}:{httpsPort}/static.html", http2=True)
    if (not code):
        target.shutdownAndExit(f"Test[Static HTTP2]: Failed! [Fatal]", exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit(f"Test[Static HTTP2]: Failed! [Got code {code}].", exitCode=EXIT.Run)
    elif version != 'HTTP/2':
        target.shutdownAndExit(f"Test[Static HTTP2]: Failed! [Got wrong version <{version}>].", exitCode=EXIT.Run)

    # 9. page opens another internet web page through a link
    target.genStdinEntropy()
    printAndLog("Test[Web page through a link]: Web page opens another internet web page through a link", doPrint=False,
                tee=getSetting('appLog'))
    _, code = curlTest(target, f"https://{targetIP}:{httpsPort}/index.html",
                       extra=[ "Host: https://www.wikipedia.org/"],http2=True)
    if (not code):
        target.shutdownAndExit(f"Test[Web page through a link]: Failed! [Fatal]", exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit(f"Test[Web page through a link]: Failed! [Got code {code}].", exitCode=EXIT.Run)

    # 10. page receives a request and saves on the local filesystem
    target.genStdinEntropy()
    printAndLog("Test[Upload text file]: Web page receives a request and saves on the local filesystem",
                doPrint=False, tee=getSetting('appLog'))
    size_upload, code = curlTest(target, f"http://{targetIP}:{httpPort}/upload",
                       extra=["-F", "file_upload=@config.ini", "-F", "press=Upload", "--write-out",
                              '%{size_upload} %{http_code}', "--silent","--output","/dev/null"],
                                 method="POST", rawOutput=True)
    if (not code):
        target.shutdownAndExit(f"Test[Upload text file]: Failed! [Fatal]", exitCode=EXIT.Run)
    elif code != '200':
        target.shutdownAndExit(f"Test[Upload text file]: Failed! [Got code {code}].", exitCode=EXIT.Run)

    printAndLog(f"Test[Upload text file]:The total amount of bytes that were uploaded is: {size_upload}.",
                doPrint=False, tee=getSetting('appLog'))

    printAndLog("Nginx tests OK!",tee=getSetting('appLog'))

    return
