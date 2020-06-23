#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *
from fett.apps.unix.webserver import curlTest
from fett.apps.unix.database import sqliteCmd
import string, secrets, crypt
import json

@decorate.debugWrap
@decorate.timeWrap
def clear_voter_table(target, dbfile):
    appLog = getSetting('appLog')
    sqlite   = "/usr/bin/sqlite"
    sqliteCmd(target, sqlite, dbfile, "DELETE FROM voter;", tee=appLog)

@decorate.debugWrap
@decorate.timeWrap
def add_official(target, dbfile):
    appLog = getSetting('appLog')
    sqlite   = "/usr/bin/sqlite"

    officialName = "official"

    # Generate the password and its hash
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    password = ''.join(secrets.choice(alphabet) for i in range(14))
    salt     = crypt.mksalt()
    passHash = crypt.crypt(password, salt)

    # Insert the record. The database will always be empty at this point,
    # so we give the official ID 0
    insert = f"INSERT INTO electionofficial (id, username, hash) VALUES (0, '{officialName}', '{passHash}');"
    sqliteCmd(target, sqlite, dbfile, insert, tee=appLog)
    select = f"SELECT * from electionofficial WHERE id = 0;"
    sqliteCmd(target, sqlite, dbfile, select, tee=appLog, 
              expectedContents=f"{passHash}")
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
def deploymentTest (target):
    printAndLog("Testing voting server...",tee=getSetting('appLog'))
    ip = target.ipTarget

    if not target.hasHardwareRNG():
        target.genStdinEntropy()
    req  = f"http://{ip}:{target.votingHttpPortTarget}/bvrs/voter_register.json?"
    req += "voter-birthdate=1986-02-04&"
    req += "voter-lastname=l&"
    req += "voter-givennames=g&"
    req += "voter-resaddress=a&"
    req += "voter-resaddress2=a2&"
    req += "voter-reszip=00000&"
    req += "voter-resstate=ZZ&"
    req += "voter-mailaddress=o&"
    req += "voter-mailaddress2=o2&"
    req += "voter-mailzip=00000&"
    req += "voter-mailstate=ZZ&"
    req += "voter-registeredparty=t&"
    req += "voter-idinfo=blob&"
    req += "voter-confidential=0"
    out = curlRequest(req, rawOutput=True)
    if out != '{}':
        target.shutdownAndExit(f"Test[Register Voter]: Failed! [Fatal]", exitCode=EXIT.Run)
    if not target.hasHardwareRNG():
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
        target.shutdownAndExit (f"Test[Check Voter]: Failed! [Malformed Result]", exc=exc, exitCode=EXIT.Run)

    printAndLog("Clearing voting database")
    clear_voter_table(target, "/var/www/data/bvrs.db")

    printAndLog("Voting tests OK!",tee=getSetting('appLog'))

    return

