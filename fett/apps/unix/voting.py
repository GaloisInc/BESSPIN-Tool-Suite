#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *
from fett.apps.unix.webserver import curlTest
import string, secrets, crypt
import json

@decorate.debugWrap
@decorate.timeWrap
def clear_voter_table(target, dbfile):
    appLog = getSetting('appLog')
    sqlite   = "/usr/bin/sqlite"
    target.runCommand(f"{sqlite} {dbfile}", expectedContents=["SQLite version", ".help"],
                      erroneousContents=["Error:","near","error"], endsWith="sqlite>",tee=appLog)
    target.runCommand("DELETE FROM voter;",
                      endsWith="sqlite>", erroneousContents=["Error:", "near", "error"],tee=appLog)
    target.runCommand(".exit",tee=appLog)

@decorate.debugWrap
@decorate.timeWrap
def add_official(target, dbfile):
    appLog = getSetting('appLog')
    sqlite   = "/usr/bin/sqlite"

    officialName = "official"

    # Generate the password and its hash
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    password = ''.join(secrets.choice(alphabet) for i in range(14))
    salt     = "XY"
    passHash = crypt.crypt(password, salt)

    # Insert the record. The database will always be empty at this point,
    # so we give the official ID 0
    target.runCommand(f"{sqlite} {dbfile}", expectedContents=["SQLite version", ".help"],
                      erroneousContents=["Error:","near","error"], endsWith="sqlite>",tee=appLog)
    target.runCommand(f"INSERT INTO electionofficial (id, username, hash) VALUES (0, \"{officialName}\", \"{passHash}\");",
                      endsWith="sqlite>", tee=appLog)
    target.runCommand(".exit",tee=appLog)

    printAndLog(f"Added election official with username '{officialName}' and password '{password}'")

@decorate.debugWrap
@decorate.timeWrap
def install (target):
    appLog = getSetting('appLog')
    printAndLog("Installing voting server")
    wwwUser = "www" if isEqSetting('osImage', 'FreeBSD') else "www-data"

    target.runCommand("mkdir -p /var/www/run",tee=appLog)
    target.runCommand("mkdir -p /var/www/cgi-bin",tee=appLog)
    target.runCommand("mkdir -p /var/www/html",tee=appLog)
    target.runCommand("mkdir -p /var/www/data",tee=appLog)

    printAndLog("Adding a new election official")
    add_official(target, "bvrs.db")

    target.runCommand("install kfcgi /usr/local/sbin/kfcgi", erroneousContents="install:",tee=appLog)
    target.runCommand("install bvrs /var/www/cgi-bin/bvrs", erroneousContents="install:",tee=appLog)

    # This is important: restrict access to the database to the 'www' user.
    target.runCommand(f"chmod 770 /var/www/data", tee=appLog)
    target.runCommand(f"chown {wwwUser}:{wwwUser} /var/www/data", tee=appLog)
    target.runCommand(f"install -m 770 -g {wwwUser} -o {wwwUser} bvrs.db /var/www/data/bvrs.db", erroneousContents="install:",tee=appLog)

    target.runCommand("echo \"Starting BVRS CGI Handler...\"",tee=appLog)

    target.runCommand(f"/usr/local/sbin/kfcgi -s /var/www/run/httpd.sock -U {wwwUser} -u {wwwUser} -p / -- /var/www/cgi-bin/bvrs /var/www/data/bvrs.db",tee=appLog)
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
def deploymentTest (target):
    printAndLog("Testing voting server...",tee=getSetting('appLog'))
    ip = target.ipTarget

    target.genStdinEntropy()
    req  = f"http://{ip}:{target.votingHttpPortTarget}/bvrs/voter_register.json?"
    req += "voter-birthdate=1986-02-04&"
    req += "voter-lastname=l&"
    req += "voter-givennames=g&"
    req += "voter-resaddress=a&"
    req += "voter-mailaddress=o&"
    req += "voter-registeredparty=t&"
    req += "voter-idinfo=blob"
    out = curlRequest(req, rawOutput=True)
    if not out:
        target.shutdownAndExit(f"Test[Register Voter]: Failed! [Fatal]", exitCode=EXIT.Run)

    target.genStdinEntropy()
    req  = f"http://{ip}:{target.votingHttpPortTarget}/bvrs/voter_check_status.json?"
    req += "voter-birthdate=1986-02-04&"
    req += "voter-lastname=l&"
    req += "voter-givennames=g"
    out = curlRequest(req, rawOutput=True)
    if not out:
        target.shutdownAndExit(f"Test[Register Voter]: Failed! [Fatal]", exitCode=EXIT.Run)
    try:
        res = json.loads(out)
        if "voter_q" not in res:
            target.shutdownAndExit(f"Test[Check Voter]: Failed! [Unexpected Result Type]", exitCode=EXIT.Run)
        if len(res["voter_q"]) != 1:
            target.shutdownAndExit(f"Test[Check Voter]: Failed! [Unexpected Contents]", exitCode=EXIT.Run)
    except json.JSONDecodeError as exc:
        target.shutdownAndExit (f"Test[Check Voter]: Failed! [Malformed Result]", exc=exc, doPrint=False)

    printAndLog("Clearing voting database")
    clear_voter_table(target, "/var/www/data/bvrs.db")

    printAndLog("Voting tests OK!",tee=getSetting('appLog'))

    return

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest (target):
    # Fill this in once the server is fully implemented
    deploymentTest (target)
    return
