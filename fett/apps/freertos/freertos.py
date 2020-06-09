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
    return (clval, codeval)

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    deploymentTest(target)

@decorate.debugWrap
@decorate.timeWrap
def HTTPSmokeTest(target, GETFileName, assetFileName, expectedCode, TCNum, TCDesc):
    # GETFileName is the name to request from the HTTP Server
    # assetFileName is the name of file against which the returned data is compared.

    targetIP = target.ipTarget
    httpPort = target.httpPortTarget

    # Find the length of the refererence asset file
    if (expectedCode == WEB_NOT_FOUND):
        expectedFileLength = 0
    else:
        try:
            filePath = os.path.join(getSetting('assetsDir'),assetFileName)
            expectedFileLength = os.stat(filePath).st_size
        except Exception as exc:
            errorAndLog (f"Failed to find length of file: <{filePath}>", exc=exc, doPrint=False)
            expectedFileLength = 0

    # Issue an HTTP GET Request for GETFilename
    contentLength,code = curlTest(target, f"http://{targetIP}:{httpPort}/{GETFileName}")
    if (code == 0):
        rtosShutdownAndExit(target, f"Test[HTTP]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code == expectedCode:
        getSetting('appLog').write(f"(Host)~  HTTP request returned code {code} and Content-Length {contentLength}.\n")

        if (expectedCode == WEB_REPLY_OK):

            if (contentLength == expectedFileLength):
                printAndLog(f"HTTP SmokeTest Case {TCNum} - {TCDesc} - PASSED",doPrint=True,tee=getSetting('appLog'))
            else:
                rtosShutdownAndExit(target, f"(Host)~  HTTP GET for {GETFileName} FAILED - Wrong length\n",exitCode=EXIT.Run)

        elif (expectedCode == WEB_NOT_FOUND):
            printAndLog(f"HTTP SmokeTest Case {TCNum} - {TCDesc} - PASSED",doPrint=True,tee=getSetting('appLog'))
        else:
            rtosShutdownAndExit(target, f"(Host)~  HTTP GET for {GETFileName} Failed! [Got code {code}].",exitCode=EXIT.Run)
    else:
        rtosShutdownAndExit(target, f"(Host)~  HTTP GET for {GETFileName} Failed! [Got code {code}].",exitCode=EXIT.Run)
    return

@decorate.debugWrap
@decorate.timeWrap
def OTATest(clientTftp, fileName, TCNum, TCDesc):
    filePath = os.path.join(getSetting('assetsDir'),fileName)
    getSetting('appLog').write(f"(Host)~  OTA SmokeTest Case {TCNum} - SEND {fileName}, {TCDesc}\n")
    try:
        clientTftp.upload(fileName, filePath, timeout=10)
        # No exception? Then...
        getSetting('appLog').write(f"(Host)~  {filePath} uploaded to the TFTP server.\n")
        printAndLog(f" OTA SmokeTest Case {TCNum} - {TCDesc} - PASSED",doPrint=True,tee=getSetting('appLog'))
    except Exception as exc:
        # some test cases as supposed to fail and reach here, so we do not mark this as
        # an error
        printAndLog(f"clientTftp: Failed to upload <{filePath}> to the server.",doPrint=False,tee=getSetting('appLog'))


@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    # target is a fett target object
    targetIP = target.ipTarget

    # Wait till TFTP server is up
    rtosRunCommand(target,"tftpServerReady",endsWith='<TFTP-SERVER-READY>',timeout=30)
    # Creating a client - this does not throw an exception as it does not connect. It is jsust an initialization.
    clientTftp = tftpy.TftpClient(targetIP, getSetting('TFTPPortTarget'))


    printAndLog ("Starting HTTP Smoketests.",doPrint=True,tee=getSetting('appLog'))

    ###################################
    # SmokeTests for the HTTP Server
    ###################################
    getSetting('appLog').write(f"(Host)~  HTTP SmokeTest Case 1 - GET index.htm\n")
    HTTPSmokeTest(target, 'index.htm', 'index.htm', WEB_REPLY_OK, 1, 'TTY, UART, HTTP')

    OtaFile = f"{getSettingDict('freertosAssets',['otaHtml'])}"
    getSetting('appLog').write(f"(Host)~  HTTP SmokeTest Case 2 - GET ota.htm\n")
    HTTPSmokeTest(target, OtaFile, OtaFile, WEB_REPLY_OK, 2, 'HTTP GET')

    # Now try a file that we know won't be there on the target. We should get error code WEB_NOT_FOUND
    getSetting('appLog').write(f"(Host)~  HTTP SmokeTest Case 3 - GET notthere.htm\n")
    HTTPSmokeTest(target, 'notthere.htm', 'notthere.htm', WEB_NOT_FOUND, 3, 'HTTP GET missing file')

    # Now try to GET glogo.png - a larger binary format file
    getSetting('appLog').write(f"(Host)~  HTTP SmokeTest Case 4 - GET glogo.png\n")
    HTTPSmokeTest(target, 'glogo.png', 'glogo.png', WEB_REPLY_OK, 4, 'HTTP GET PNG file')


    ###################################
    # SmokeTests for the OTA Server
    ###################################

    logging.getLogger('tftpy').propagate = False
    logging.getLogger('tftpy').addHandler(logging.FileHandler(os.path.join(getSetting('workDir'),'tftpy.out'),'w'))

    printAndLog ("Starting OTA Smoketests.",doPrint=True,tee=getSetting('appLog'))

    # uploading the signed ota.htm file
    OTATest(clientTftp, f"{getSettingDict('freertosAssets',['otaHtml'])}.sig", 1, 'OTA, Crypto, Filesystem')

    # uploading the signed ota.htm file AGAIN
    OTATest(clientTftp, f"{getSettingDict('freertosAssets',['otaHtml'])}.sig", 2, 'OTA, Crypto, Filesystem')

    # uploading the signed badsig.htm file - Signature is corrupt
    OTATest(clientTftp, "badsig.htm.sig", 3, 'OTA corrupt signature')

    # uploading ota512.htm.sig - exactly 1 TFTP block...
    OTATest(clientTftp, "ota512.htm.sig", 4, 'OTA, TFTP 1 block')
    # ...and fetch it back from the HTTP server - note the filename changes to ota.htm
    # on the HTTP server. We should get back 448 bytes (512 minus the 64 byte signature)
    HTTPSmokeTest(target, OtaFile, "ota512.htm", WEB_REPLY_OK, 5, 'Roundtrip OTA TC 4')

    # uploading ota65535.htm.sig - just under the upper limit for our server.
    OTATest(clientTftp, "ota65535.htm.sig", 5, 'OTA just below max file size')
    HTTPSmokeTest(target, OtaFile, "ota65535.htm", WEB_REPLY_OK, 6, 'Roundtrip OTA TC 5')

    # uploading ota65536.htm.sig - the upper limit for our server.
    # Should be rejected
    OTATest(clientTftp, "ota65536.htm.sig", 6, 'OTA exactly max file size')
    # OtaFile should NOT have been changed, so check it's still as was
    HTTPSmokeTest(target, OtaFile, "ota65536.htm", WEB_REPLY_OK, 7, 'Roundtrip OTA TC 6')

    # Restore the original ota.htm file
    OTATest(clientTftp, f"{getSettingDict('freertosAssets',['otaHtml'])}.sig", 7, 'Restore original OTA state')

    # uploading ota65537.htm.sig - the upper limit for our server.
    # Should be rejected
    OTATest(clientTftp, "ota65537.htm.sig", 8, 'OTA too large file')
    # OtaFile should NOT have been changed, so check it's still as was
    HTTPSmokeTest(target, OtaFile, OtaFile, WEB_REPLY_OK, 8, 'Verify FS not changed by OTA TC 8')


    ###################################
    # STOP the FreeRTOS application
    # uploading the signed stop.htm file
    ###################################
    fileName = f"{getSettingDict('freertosAssets',['StopHtml'])}.sig"
    filePath = os.path.join(getSetting('assetsDir'),fileName)
    printAndLog ("Sending STOP message via OTA.",doPrint=True,tee=getSetting('appLog'))
    try:
        clientTftp.upload(fileName, filePath, timeout=10)
    except Exception as exc:
        rtosShutdownAndExit(target, f"clientTftp: Failed to upload <{filePath}> to the server.",exc=exc,exitCode=EXIT.Run)
    getSetting('appLog').write(f"\n(Host)~  {filePath} uploaded to the TFTP server.")


    # downloading a file - NOT IMPLEMENTED ON TARGET YET
    # fileName = "fileToReceive.html"
    # fileToReceive = os.path.join(getSetting('workDir'),fileName)
    # try:
    #    clientTftp.download(filename, output, packethook=None, timeout=10)
    # except Exception as exc:
    #    rtosShutdownAndExit(target, f"clientTftp: Failed to download <{fileToReceive}> from the server.",exc=exc,exitCode=EXIT.Run)


    # Run to completion
    rtosRunCommand(target,"runFreeRTOSapps",endOfApp=True,timeout=20)
    return

@decorate.debugWrap
def rtosRunCommand (target,command,endsWith=[],expectedContents=None,erroneousContents=[],shutdownOnError=True,timeout=60,suppressErrors=False,expectExact=False,endOfApp=False):
    if isinstance(endsWith,str):
        endsWith = [endsWith]
    elif (not isinstance(endsWith,list)):
        rtosShutdownAndExit(target, f"rtosRunCommand: <endsWith> has to be list or str.",exitCode=EXIT.Dev_Bug)

    if (isinstance(erroneousContents,str)):
        erroneousContents = [erroneousContents]
    elif (not isinstance(erroneousContents,list)):
        rtosShutdownAndExit(target, f"rtosRunCommand: <erroneousContents> has to be list or str.",exitCode=EXIT.Dev_Bug)

    retCommand = target.runCommand(command,endsWith=[">>>End of Fett<<<"] + endsWith,
        expectedContents=expectedContents,erroneousContents=erroneousContents + ['(Error)','EXIT: exiting FETT with code <1>'],shutdownOnError=shutdownOnError,
        timeout=timeout,suppressErrors=suppressErrors,expectExact=expectExact,tee=getSetting('appLog'))

    if ((retCommand[3] == 0) and (not endOfApp)): #FETT exited prematurely
        target.shutdownAndExit(f"rtosRunCommand: FreeRTOS finished prematurely.",exitCode=EXIT.Run)

    return

@decorate.debugWrap
def rtosShutdownAndExit (target, message, exc=None, exitCode=None):
    # Run to completion
    rtosRunCommand(target,"endFreeRTOSapps",endOfApp=True,shutdownOnError=False,timeout=30)
    target.shutdownAndExit(message, exc=exc, exitCode=exitCode)

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
