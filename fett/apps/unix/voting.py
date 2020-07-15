#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute this app
"""

from fett.base.utils.misc import *
from fett.apps.unix.webserver import curlTest
from fett.apps.unix.database import sqliteCmd
import string, secrets, crypt, base64
import json, os

@decorate.debugWrap
@decorate.timeWrap
def add_official(target, dbfile):
    appLog = getSetting('appLog')
    sqlite   = getSetting('sqliteBin')

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
              expectedContents="0|official|") # expecting the hash causes issues with FreeBSD
    printAndLog(f"Added election official with username '{officialName}' and password '{password}'")


@decorate.debugWrap
@decorate.timeWrap
def install (target):
    if (isEqSetting('binarySource','SRI-Cambridge')):
        prefix = "/fett/var"
        # Add the voting password to the logs
        retCatPassword = target.runCommand("cat /root/bvrs-official-password")[1]
        passwordMatch = matchExprInLines (r"^(?P<b64Password>[A-Za-z0-9+/]{16})$",retCatPassword.splitlines())
        if (not passwordMatch):
            target.shutdownAndExit("<sriCambdridgeSetup>: Failed to obtain the election official password.",exitCode=EXIT.Run)
        printAndLog(f"The election official credentials are: username 'official' and password '{passwordMatch.group('b64Password')}'")
        return
    else:
        prefix = "/var"
    appLog = getSetting('appLog')
    printAndLog("Installing voting server")
    wwwUser = "www" if isEqSetting('osImage', 'FreeBSD') else "www-data"

    target.runCommand(f"mkdir -p {prefix}/www/run",tee=appLog)
    target.runCommand(f"mkdir -p {prefix}/www/cgi-bin",tee=appLog)
    target.runCommand(f"mkdir -p {prefix}/www/bvrs/bvrs",tee=appLog)
    target.runCommand(f"mkdir -p {prefix}/www/data",tee=appLog)
    target.runCommand("mkdir -p /etc/ssl/certs",tee=appLog)
    target.runCommand("mkdir -p /etc/ssl/private",tee=appLog)

    target.runCommand("cp -r certs/* /etc/ssl/certs",tee=appLog)
    target.runCommand("cp -r keys/* /etc/ssl/private",tee=appLog)


    target.runCommand("install kfcgi /usr/local/sbin/kfcgi", erroneousContents="install:",tee=appLog)
    target.runCommand(f"install bvrs {prefix}/www/cgi-bin/bvrs", erroneousContents="install:",tee=appLog)
    target.runCommand(f"install static/index.html {prefix}/www/bvrs", erroneousContents="install:",tee=appLog)
    target.runCommand(f"install static/bvrs/* {prefix}/www/bvrs/bvrs", erroneousContents="install:",tee=appLog)

    printAndLog("Adding a new election official")
    add_official(target, "bvrs.db")
    
    target.runCommand("install kfcgi /usr/local/sbin/kfcgi", erroneousContents="install:",tee=appLog)
    target.runCommand("install bvrs /var/www/cgi-bin/bvrs", erroneousContents="install:",tee=appLog)

    # This is important: restrict access to the database to the 'www' user.
    target.runCommand(f"chmod 770 {prefix}/www/data", tee=appLog)
    target.runCommand(f"chown {wwwUser}:{wwwUser} /var/www/data", tee=appLog)

    target.runCommand(f"install -m 770 -g {wwwUser} -o {wwwUser} bvrs.db {prefix}/www/data/bvrs.db", erroneousContents="install:",tee=appLog)

    target.runCommand("echo \"Starting BVRS CGI Handler...\"",tee=appLog)

    if isEqSetting('osImage', 'debian'):
        target.runCommand("install bvrs.service /lib/systemd/system/bvrs.service", erroneousContents="install:", tee=appLog)
        target.runCommand("systemctl enable bvrs.service", tee=appLog)
        target.runCommand("systemctl start bvrs.service", erroneousContents=["Failed to start", "error code"], tee=appLog)
    elif isEqSetting('osImage', 'FreeBSD'):
        target.runCommand(f"/usr/local/sbin/kfcgi -s {prefix}/www/run/httpd.sock -U {wwwUser} -u {wwwUser} -p / -- {prefix}/www/cgi-bin/bvrs {prefix}/www/data/bvrs.db",tee=appLog)
    else:
        target.shutdownAndExit (f"Can't start bvrs service on <{getSetting('osImage')}>", exitCode=EXIT.Dev_Bug)
    return

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest (target):
    printAndLog("Testing voting server...",tee=getSetting('appLog'))
    ip = target.ipTarget

    if not target.hasHardwareRNG():
        target.genStdinEntropy()
    req  = f"http://{ip}:{target.votingHttpPortTarget}/bvrs/voter_register.json?"
    req += "voter-birthdate=1900-01-01&"
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
    req += "voter-birthdate=1900-01-01&"
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

    printAndLog("Unregistering test voter")
    sqlite = getSetting('sqliteBin')
    appLog = getSetting('appLog')    
    if (isEqSetting('binarySource','SRI-Cambridge')):
      prefix = "/fett/var"
    else:
      prefix = "/var"
    dbfile = f"{prefix}/www/data/bvrs.db"
    sql = f"DELETE FROM voter WHERE birthdate='1900-01-01' and lastname='l' and givennames='g';"
    sqliteCmd(target, sqlite, dbfile, sql, tee=appLog, 
              expectedContents="")

    printAndLog("Voting tests OK!",tee=getSetting('appLog'))

    return

