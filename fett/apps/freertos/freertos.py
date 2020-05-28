#! /usr/bin/env python3
""" 
This is executed after loading the app on the target to execute FreeRTOS app
"""

from fett.base.utils.misc import *  
import tftpy, os, re

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
def curlTest(target, url, extra=[], http2=False):
    printAndLog(f"curl {url} extra={extra} http2={http2}", doPrint=False,tee=getSetting('appLog'))
    out = curlRequest(url, http2=http2, extra=extra, rawOutput=False)
    if (not out):
        return (None,None)
    try:
        printAndLog(f"curl {url} returned:\n{out}\n", doPrint=False,tee=getSetting('appLog'))

        # Line 0 of "out" should be something like "HTTP/1.1 200 OK".
        # We're mainly interested in the middle one - the return status code
        version,code,*rest = out.splitlines()[0].split(' ')

        # Line 3 of "out" should be of the form "Content-Length: XXX"
        # where XXX is a positive integer.  We want to grab that and report it back to the caller
        clheader,contentLength = out.splitlines()[3].split(' ')

    except Exception as exc:
        errorAndLog (f"Failed to parse curl output: <{out}>", exc=exc, doPrint=False)
        return (None,None)
    printAndLog(f"curl {url} extra={extra} http2={http2} returned code {code}, Content-Length {contentLength}\n", doPrint=False,tee=getSetting('appLog'))
    return (contentLength, code)

@decorate.debugWrap
@decorate.timeWrap
def extensiveTest(target):
    deploymentTest(target)

@decorate.debugWrap
@decorate.timeWrap
def deploymentTest(target):
    # target is a fett target object
    targetIP = target.ipTarget
    httpPort = target.httpPortTarget

    # Wait till TFTP server is up
    rtosRunCommand(target,"tftpServerReady",endsWith='<TFTP-SERVER-READY>',timeout=30)
    # Creating a client - this does not throw an exception as it does not connect. It is jsust an initialization.
    clientTftp = tftpy.TftpClient(targetIP, getSetting('TFTPPortTarget')) 

    # uploading the signed ota.htm file
    fileName = f"{getSettingDict('freertosAssets',['otaHtml'])}.sig"
    filePath = os.path.join(getSetting('assetsDir'),fileName)
    try:
        clientTftp.upload(fileName, filePath, timeout=10)
    except Exception as exc:
        target.shutdownAndExit(f"clientTftp: Failed to upload <{filePath}> to the server.",exc=exc,exitCode=EXIT.Run)
    getSetting('appLog').write(f"\n(Host)~  {filePath} uploaded to the TFTP server.\n")


    # Issue an HTTP GET Request for index.htm
    filePath = os.path.join(getSetting('assetsDir'),'index.htm')
    expectedFileLength = os.stat(filePath).st_size
    getSetting('appLog').write(f"(Host)~  HTTP Request expected length is {expectedFileLength}.\n")

    contentLength,code = curlTest(target, f"http://{targetIP}:{httpPort}/index.htm")
    if (not code):
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Fatal]",exitCode=EXIT.Run)
    elif code == '200':
        getSetting('appLog').write(f"(Host)~  HTTP request returned code {code} and Content-Length {contentLength}.\n")

        # contentLength is a string, but expectedFileLength is an int, so to compare...
        if (int(contentLength) == expectedFileLength):
            getSetting('appLog').write(f"(Host)~  HTTP TEST PASSED\n")
        else:
            getSetting('appLog').write(f"(Host)~  HTTP TEST FAILED - Wrong length\n")
    else:
        target.shutdownAndExit (f"Test[HTTP]: Failed! [Got code {code}].",exitCode=EXIT.Run)

    # uploading the signed stop.htm file
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
