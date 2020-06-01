#! /usr/bin/env python3
"""
This is executed after loading the app on the target to execute FreeRTOS app
"""

from fett.base.utils.misc import *
import tftpy, os, re
import logging

# HTTP Status code constants. These must match those in http_commands.h
WEB_REPLY_OK = 200
WEB_NOT_FOUND = 404

@decorate.debugWrap
@decorate.timeWrap
def install (target):
    return

@decorate.debugWrap
@decorate.timeWrap
def deploy(target):
    printAndLog ("Deployment successful. Target is ready.",tee=getSetting('appLog'))

    #Here we should send a message to the portal

    #Here we should wait for a termination signal from the portal

    printAndLog("Termination signal received. Preparing to exit...",tee=getSetting('appLog'))
    return

@decorate.debugWrap
@decorate.timeWrap
# returns a pair of integers (X,Y).
# X is the Content-Length field, only valid when Y = WEB_REPLY_OK
# Y is the HTTP reponse status code, such as WEB_REPLY_OK or WEB_NOT_FOUND
# Returns (0,0) on error
def curlTest(target, url, extra=[], http2=False):
    printAndLog(f"(Host)~  curl {url} extra={extra} http2={http2}", doPrint=False,tee=getSetting('appLog'))
    out = curlRequest(url, http2=http2, extra=extra, rawOutput=False)
    if (not out):
        return (0,0)
    try:
        # Line 0 of "out" should be something like "HTTP/1.1 200 OK".
        # We're mainly interested in the middle one - the return status code
        try:
            version,code,*rest = out.splitlines()[0].split(' ')
            codeval = int(code)
        except Exception as exc:
            errorAndLog (f"Failed to find status code field in: <{out}>", exc=exc, doPrint=False)
            codeval = 0

        # A successful request should also have a Content-Length field
        if (codeval == WEB_REPLY_OK):
            # Line 3 of "out" should be of the form "Content-Length: XXX"
            # where XXX is a positive integer.  We want to grab that and report it back to the caller
            try:
                clheader,contentLength = out.splitlines()[3].split(' ')
                clval = int(contentLength)
            except Exception as exc:
                errorAndLog (f"Failed to find Content-Length field in: <{out}>", exc=exc, doPrint=False)
                clval = 0
        else:
            clval = 0
    except Exception as exc:
        errorAndLog (f"Failed to parse curl output: <{out}>", exc=exc, doPrint=False)
        return (0,0)
    return (clval, codeval)

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    deploymentTest(target)

@decorate.debugWrap
@decorate.timeWrap
def HTTPSmokeTest(target, assetFileName, expectedCode):
    # Issue an HTTP GET Request for assetFilename
    targetIP = target.ipTarget
    httpPort = target.httpPortTarget

    if (expectedCode == WEB_NOT_FOUND):
        expectedFileLength = 0
    else:
        try:
            filePath = os.path.join(getSetting('assetsDir'),assetFileName)
            expectedFileLength = os.stat(filePath).st_size
        except Exception as exc:
            errorAndLog (f"Failed to find length of file: <{filePath}>", exc=exc, doPrint=False)
            expectedFileLength = 0

    contentLength,code = curlTest(target, f"http://{targetIP}:{httpPort}/{assetFileName}")
    if (code == 0):
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code == expectedCode:
        getSetting('appLog').write(f"(Host)~  HTTP request returned code {code} and Content-Length {contentLength}.\n")

        if (expectedCode == WEB_REPLY_OK):

            if (contentLength == expectedFileLength):
                getSetting('appLog').write(f"(Host)~  HTTP GET for {assetFileName} PASSED\n")
            else:
                logAndExit(f"(Host)~  HTTP GET for {assetFileName} FAILED - Wrong length\n")

        elif (expectedCode == WEB_NOT_FOUND):
            getSetting('appLog').write(f"(Host)~  HTTP GET for {assetFileName} PASSED\n")
        else:
            target.shutdownAndExit (f"(Host)~  HTTP GET for {assetFileName} Failed! [Got code {code}].",exitCode=EXIT.Run)
    else:
        target.shutdownAndExit (f"(Host)~  HTTP GET for {assetFileName} Failed! [Got code {code}].",exitCode=EXIT.Run)
    return

@decorate.debugWrap
@decorate.timeWrap
def OTATest(clientTftp, fileName, testCase):
    filePath = os.path.join(getSetting('assetsDir'),fileName)
    getSetting('appLog').write(f"(Host)~  OTA SmokeTest Case {testCase} - SEND {fileName}\n")
    try:
        clientTftp.upload(fileName, filePath, timeout=10)
    except Exception as exc:
        # This test case reaches here with an unknown exception
        errorAndLog(f"clientTftp: Failed to upload <{filePath}> to the server.",doPrint=True,exc=exc)
    getSetting('appLog').write(f"(Host)~  {filePath} uploaded to the TFTP server.\n")


@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    # target is a fett target object
    targetIP = target.ipTarget

    # Wait till TFTP server is up
    rtosRunCommand(target,"tftpServerReady",endsWith='<TFTP-SERVER-READY>',timeout=30)
    # Creating a client - this does not throw an exception as it does not connect. It is jsust an initialization.
    clientTftp = tftpy.TftpClient(targetIP, getSetting('TFTPPortTarget'))

    ###################################
    # SmokeTests for the HTTP Server
    ###################################
    getSetting('appLog').write(f"(Host)~  HTTP SmokeTest Case 1 - GET index.htm\n")
    HTTPSmokeTest(target, 'index.htm', WEB_REPLY_OK)

    getSetting('appLog').write(f"(Host)~  HTTP SmokeTest Case 2 - GET ota.htm\n")
    HTTPSmokeTest(target, f"{getSettingDict('freertosAssets',['otaHtml'])}", WEB_REPLY_OK)

    # Now try a file that we know won't be there on the target. We should get error code WEB_NOT_FOUND
    getSetting('appLog').write(f"(Host)~  HTTP SmokeTest Case 3 - GET notthere.htm\n")
    HTTPSmokeTest(target, 'notthere.htm', WEB_NOT_FOUND)

    # Now try to GET glogo.png - a larger binary format file
    getSetting('appLog').write(f"(Host)~  HTTP SmokeTest Case 4 - GET glogo.png\n")
    HTTPSmokeTest(target, 'glogo.png', WEB_REPLY_OK)


    ###################################
    # SmokeTests for the OTA Server
    ###################################

    logging.getLogger('tftpy').propagate = False
    logging.getLogger('tftpy').addHandler(logging.FileHandler(os.path.join(getSetting('workDir'),'tftpy.out'),'w'))

    # uploading the signed ota.htm file
    OTATest(clientTftp, f"{getSettingDict('freertosAssets',['otaHtml'])}.sig", 1)

    # uploading the signed ota.htm file AGAIN
    OTATest(clientTftp, f"{getSettingDict('freertosAssets',['otaHtml'])}.sig", 2)

    # uploading the signed badsig.htm file - Signature is corrupt
    OTATest(clientTftp, "badsig.htm.sig", 3)

    # upload file with 129 character file name
    OTATest(clientTftp, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab.htm.sig", 4)

    ###################################
    # STOP the FreeRTOS application
    # uploading the signed stop.htm file
    ###################################
    fileName = f"{getSettingDict('freertosAssets',['StopHtml'])}.sig"
    filePath = os.path.join(getSetting('assetsDir'),fileName)
    try:
        clientTftp.upload(fileName, filePath, timeout=10)
    except Exception as exc:
        target.shutdownAndExit(f"clientTftp: Failed to upload <{filePath}> to the server.",exc=exc,exitCode=EXIT.Run)
    getSetting('appLog').write(f"\n(Host)~  {filePath} uploaded to the TFTP server.")


    # downloading a file - NOT IMPLEMENTED ON TARGET YET
    # fileName = "fileToReceive.html"
    # fileToReceive = os.path.join(getSetting('workDir'),fileName)
    # try:
    #    clientTftp.download(filename, output, packethook=None, timeout=10)
    # except Exception as exc:
    #    target.shutdownAndExit(f"clientTftp: Failed to download <{fileToReceive}> from the server.",exc=exc,exitCode=EXIT.Run)


    # Run to completion
    rtosRunCommand(target,"runFreeRTOSapps",endOfApp=True,timeout=getSetting('appTimeout'))
    return

def rtosRunCommand (target,command,endsWith=[],expectedContents=None,erroneousContents=[],shutdownOnError=True,timeout=60,suppressErrors=False,expectExact=False,endOfApp=False):
    if isinstance(endsWith,str):
        endsWith = [endsWith]
    elif (not isinstance(endsWith,list)):
        target.shutdownAndExit(f"rtosRunCommand: <endsWith> has to be list or str.",exitCode=EXIT.Dev_Bug)

    if (isinstance(erroneousContents,str)):
        erroneousContents = [erroneousContents]
    elif (not isinstance(erroneousContents,list)):
        target.shutdownAndExit(f"rtosRunCommand: <erroneousContents> has to be list or str.",exitCode=EXIT.Dev_Bug)

    retCommand = target.runCommand(command,endsWith=[">>>End of Fett<<<"] + endsWith,
        expectedContents=expectedContents,erroneousContents=erroneousContents + ['(Error)','EXIT: exiting FETT with code <1>'],shutdownOnError=shutdownOnError,
        timeout=timeout,suppressErrors=suppressErrors,expectExact=expectExact,tee=getSetting('appLog'))

    if ((retCommand[3] == 0) and (not endOfApp)): #FETT exited prematurely
        target.shutdownAndExit(f"rtosRunCommand: FreeRTOS finished prematurely.",exitCode=EXIT.Run)

    return


@decorate.debugWrap
def prepareAssets ():
    assetsPath = os.path.join(getSetting('repoDir'),getSettingDict('freertosAssets',['path']))
    setSetting('assetsDir',assetsPath)
    #copy the empty header to buildDir
    httpAssetsFilename = 'httpAssets.h'
    cp (os.path.join(assetsPath,httpAssetsFilename),getSetting('appLibDir'))

    assetsHfile = ftOpenFile (os.path.join(getSetting('appLibDir'),httpAssetsFilename),'a')

    #go through the assets, and: check 8.3 compatibility + dump their data into the header
    listAssets = getSettingDict('freertosAssets',['assets'])

    for xAsset in listAssets:
        #Check 8.3 compatibility -- strict check
        if (not re.match(r"\w{1,8}\.\w{3}",xAsset)):
            logAndExit (f"prepareAssets: The SD filesystem only accepts filenames in 8.3 format. The asset <{assetsPath}/{xAsset}> does not comply.")

        assetsHfile.write(fett_xxd_i(os.path.join(assetsPath,xAsset)))

    # write the asset_files macro
    assetsHfile.write(f"// assets\n")
    assetsHfile.write(f"#define asset_files {len(listAssets)}\n\n")
    # write the asset_sizes
    assetsHfile.write(f"static size_t asset_sizes[asset_files] = {{\n")
    assetsHfile.write(f"\t{','.join([xAsset.replace('.','_')+'_size' for xAsset in listAssets])}\n}};\n")
    # write the asset_names
    assetsHfile.write(f"static const char * const asset_names[asset_files] = {{\n")
    assetsHfile.write(f"\t{','.join([xAsset.replace('.','_')+'_name' for xAsset in listAssets])}\n}};\n")
    # write the asset_data
    assetsHfile.write(f"static const uint8_t * const asset_data[asset_files] = {{\n")
    assetsHfile.write(f"\t{','.join([xAsset.replace('.','_')+'_data' for xAsset in listAssets])}\n}};\n")

    assetsHfile.close()

@decorate.debugWrap
@decorate.timeWrap
def fett_xxd_i (binPath,check83=True):
    """
    # The input is a path to a file.
    # The output is similar to the output of `xxd -i binPath`.
    """
    try:
        fbin = open(binPath,"rb")
        binData = fbin.read()
        hexFormatData = [f"0x{xByte:02x}" for xByte in binData]
        fbin.close()
    except Exception as exc:
        logAndExit (f"fett_xxd_i: Failed to generate a header from <{binPath}>.",exc=exc,exitCode=EXIT.Files_and_paths)

    fileName = os.path.basename(binPath)
    filePrefix = fileName.replace('.','_')
    outXxd = f"//{fileName}\n"
    outXxd += f"#define {filePrefix}_size {len(binData)}\n"
    outXxd += f"static const char * const {filePrefix}_name = \"{fileName}\";\n"
    outXxd += f"static const uint8_t {filePrefix}_data[{filePrefix}_size] = {{\n"
    for xChunk in [hexFormatData[i:i+12] for i in range(0,len(hexFormatData),12)]:
        outXxd += '\t' + ','.join(xChunk) + ',\n'
    outXxd = outXxd[:-2] #remove the last comma
    outXxd += '\n};\n\n'

    return outXxd
