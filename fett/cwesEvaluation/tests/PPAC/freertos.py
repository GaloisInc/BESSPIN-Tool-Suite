"""
FreeRTOS prep for PPAC tests
"""

from fett.base.utils.misc import *
from fett.target.build import prepareFreeRTOSNetworkParameters
import subprocess, os, re

@decorate.debugWrap
def prepareFreeRTOSforPPAC ():
    # copy extra sources + main FreeRTOS program over
    ppacDir = os.path.join(getSetting('repoDir'),'fett','cwesEvaluation','tests','PPAC')
    sourcesDir = os.path.join(ppacDir,'sources')
    copyDir(os.path.join(sourcesDir,'libFreeRTOS'),
            os.path.join(getSetting('buildDir'),'lib_PPAC'),
            renameDest=True)
    
    # Needs fettFreeRTOSIPConfig.h
    prepareFreeRTOSNetworkParameters()

    # Certificates
    genPPACcertifications (ppacDir)
    
    # Time fixes
    #[TODO]
    
    # WolfSSL seeds
    #[TODO]

@decorate.debugWrap
def genPPACcertifications (ppacDir):
    printAndLog ("Generating CA keys and certifications for PPAC tests...")

    certsDir = os.path.join(getSetting('buildDir'),'lib_PPAC')
    shellScript = os.path.join(ppacDir,'scripts','genCertificates.sh')

    #Maybe these should be configurable options
    nCertDays=100
    shaSize=256
    rsaSize=1024
    dhSize=1024

    headersNeeded = []

    # Generate two CA certificates, one for "Jedi Order" and one for "SSITH Lord"
    caCerts = {
        'JEDI' : {
            'CN' : 'Jedi Order CA'
        },
        'SSITH' : {
            'CN' : 'SSITH Lord CA'
        }
    }

    for caCert,certInfo in caCerts.items():
        if (caCert == 'SSITH'):
            suffix = 'SSITH'
        else:
            suffix = ''
        # generate the key -- Note that the stdout of the file gets confused when using `-out`
        keyName = os.path.join(certsDir,f'caKey{suffix}.pem')
        keyFile = ftOpenFile(keyName,'w')
        stderrFile = ftOpenFile(os.path.join(getSetting('workDir'),'shell.out'),'a')
        stderrFile.write(f"Generating {keyName}...")
        stderrFile.flush()
        try:
            subprocess.run(['openssl','genrsa',f'{rsaSize}'],check=True,stdout=keyFile,stderr=stderrFile)
        except Exception as exc:
            logAndExit (f"genPPACcertifications: Failed to generate <{keyName}>. Check <shell.out> for more details.",exc=exc,exitCode=EXIT.Run)
        stderrFile.close()
        keyFile.close()
        # generate the cert
        certName = os.path.join(certsDir,f'caCert{suffix}.pem')
        headersNeeded.append(certName)

        shellCommand(['openssl','req','-new','-x509','-nodes',f'-sha{shaSize}', 
                      '-days',f'{nCertDays}','-key',keyName,
                      '-subj',f"/C=US/ST=Oregon/L=Portland/O=Galois Inc./OU=Besspin/CN={certInfo['CN']}",
                      '-out',certName
                      ]) 

    # Generate server and client certificates: 1 server + 2 clients Jedi, and 1 client SSITH
    userCerts = {
        'jediServer' : {
            'name' : 'server',
            'type' : 'JEDI',
            'CN' : 'Jedi Order SERV'
        },
        'jediClient' : {
            'name' : 'client',
            'type' : 'JEDI',
            'CN' : 'Jedi Order CLNT'
        },
        'jediClient2' : {
            'name' : 'client2',
            'type' : 'JEDI',
            'CN' : 'Yoda'
        },
        'ssithClient' : {
            'name' : 'client',
            'type' : 'SSITH',
            'CN' : 'SSITH Lord CLNT'
        }
    }

    for userCert,certInfo in userCerts.items():
        if (certInfo['type'] == 'SSITH'):
            suffix = 'SSITH'
        else:
            suffix = ''
        # key + request
        keyName = os.path.join(certsDir,f"{certInfo['name']}Key{suffix}.pem")
        headersNeeded.append(keyName)
        certName = os.path.join(certsDir,f"{certInfo['name']}Cert{suffix}.pem")
        headersNeeded.append(certName)
        reqName = f'{certName}.csr'
        shellCommand(['openssl','req','-newkey',f'rsa:{rsaSize}',f'-sha{shaSize}',
                      '-days',f'{nCertDays}','-nodes','-keyout',keyName,
                      '-subj',f"/C=US/ST=Oregon/L=Portland/O=Galois Inc./OU=Besspin/CN={certInfo['CN']}",
                      '-out', reqName
                      ])
        # The cert
        caCert = os.path.join(certsDir,f'caCert{suffix}.pem')
        caKey = os.path.join(certsDir,f'caKey{suffix}.pem')
        shellCommand(['openssl','x509','-req','-in', reqName,
                      '-days',f'{nCertDays}',f'-sha{shaSize}','-CA',caCert,
                      '-CAkey',caKey,'-set_serial','01',
                      '-out',certName
                      ]) 

    # Generate a DH public parameters -- has to be DER, but -outform does not work properly with genpkey
    dhParamFilePrefix = os.path.join(certsDir,'dhParams')
    # create the DH public parameters <dhParams.pem>
    shellCommand(['openssl','genpkey','-genparam','-algorithm','DH','-pkeyopt',f'dh_paramgen_prime_len:{dhSize}',
                  '-out', f'{dhParamFilePrefix}.pem'])
    # convert the DH public parameters <dhParams.pem> to DER format"
    headersNeeded.append(f'{dhParamFilePrefix}.der')
    shellCommand(['openssl','dhparam','-in',f'{dhParamFilePrefix}.pem','-inform','PEM',
                  '-out', f'{dhParamFilePrefix}.der','-outform','DER'])

    # Convert the files to Header files
    for inFile in headersNeeded:
        headerName = re.sub(r".(pem|der)",'.h',inFile)
        headerFile = ftOpenFile(headerName,'w')
        headerFile.write('static const ')
        headerFile.flush()
        stderrFile = ftOpenFile(os.path.join(getSetting('workDir'),'shell.out'),'a')
        stderrFile.write(f"Generating {headerName}...")
        stderrFile.flush()
        try:
            subprocess.run(['xxd','-i',os.path.basename(inFile)],check=True,
                            stdout=headerFile,stderr=stderrFile,cwd=certsDir)
        except Exception as exc:
            logAndExit (f"genPPACcertifications: Failed to generate <{keyName}>. Check <shell.out> for more details.",exc=exc,exitCode=EXIT.Run)
        stderrFile.close()
        headerFile.close()

    printAndLog (f"Keys and certificates were generated in <{certsDir}>.")
