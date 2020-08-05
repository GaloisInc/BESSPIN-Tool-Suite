#! /usr/bin/env bash
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Generate server and client certificates 
# <<following instructions in $TESTGEN/FreeRTOS-mirror/FreeRTOS-Plus/Source/WolfSSL_Galois/certs/taoCert.txt>>
# Usage: Please DO NOT USE DIRECTLY. [All sanity checks are done via testgen.sh]
# Follow instructions in testgen.sh instead
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#called like that: <thisFile> $setupEnv $BASE_DIR $id $vulClass $testsDir
fileName=`basename $0`
setupEnv=$1
BASE_DIR=$2
id=$3
vulClass=$4
testsDir=$5
source $setupEnv $BASE_DIR $id $vulClass
isError $? "Error in $fileName: Failed to load configurations for <$vulClass>." 
#------------- END of configuration

certDir=$testsDir/lib
#Maybe these should be configurable options
nCertDays=100
shaSize=256
rsaSize=1024
dhSize=1024

#Implementation choice. Not in config because some functions need to be changed accordingly.
usePEMmetadata=0
pemORder=pem

try() {
    local desc="$1"
    shift 1
    "$@" 2>> $reportFile
    isError $? "Error in $fileName: Failed to $desc"
}

expect() {
    local msg="$1"
    shift 1
    if ! "$@"; then
        isError 1 "Error in $fileName: Expected $msg"
    fi
}

expectFileType() {
    local fileDesc="$1"
    local file="$2"
    local type="$3"
    expect "$fileDesc <$file> to have type '$type'" \
        [ "$(file -b $file)" == "$type" ]
}

maybeAddPEMMetadata() {
    local file="$1"
    if [ $usePEMmetadata == 1 ]; then
        try "add human-readable certificate data to <$file>" \
            openssl x509 -in $file -text -out $file.tmp
        mv $file.tmp $file
        expectFileType "certificate" $file "ASCII text"
    fi
}

genSelfSigned() {
    local keyFile="$1"
    local certFile="$2"
    local csrFile="${certFile}.csr"
    local cnfFile="$3"
    local subj="$4"

    # Generate a config file for `openssl ca` that uses the newly generated
    # certificate.  We also use this when generating the certificate itself, as
    # otherwise it will try to write certificates into a nonexistent directory.
    cat >$cnfFile <<EOF
[ ca ]
default_ca      = CA_default            # The default ca section

[ CA_default ]

dir            = $PWD
database       = $PWD/ca-index.txt
new_certs_dir  = $PWD/newcerts

certificate    = $PWD/$certFile
serial         = $PWD/ca-serial.txt
rand_serial    = no
private_key    = $PWD/$keyFile

default_md     = sha${shaSize}
default_days   = $nCertDays

policy         = policy_any
email_in_dn    = no

name_opt       = ca_default
cert_opt       = ca_default
copy_extensions = none

[ policy_any ]
countryName            = supplied
stateOrProvinceName    = optional
localityName           = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional

EOF

    try "create the CA private key <$keyFile>" \
        openssl genrsa -out $keyFile $rsaSize
    expectFileType "private key" $keyFile "PEM RSA private key"

    try "create the CA certificate signing request <$csrFile>" \
        openssl req -new -nodes -sha${shaSize} -key $keyFile -subj "$subj" -out $csrFile
    expectFileType "certificate signing request" $csrFile "PEM certificate request"

    try "create the CA certificate <$certFile>" \
        openssl ca -batch -notext -config $cnfFile -in $csrFile \
            -extfile /etc/ssl/openssl.cnf -extensions v3_ca \
            -keyfile $keyFile -selfsign -out $certFile
    expectFileType "certificate" $certFile "PEM certificate"

    maybeAddPEMMetadata $certFile
    echo "Generated CA certificate <$certFile>" >> $reportFile
}

genUserCert() {
    local keyFile="$1"
    local certFile="$2"
    local csrFile="${certFile}.csr"
    local caCnfFile="$3"
    local subj="$4"

    try "create user private key <$keyFile>" \
        openssl genrsa -out $keyFile $rsaSize
    expectFileType "private key" $keyFile "PEM RSA private key"

    try "create user certificate signing request <$csrFile>" \
        openssl req -new -nodes -sha${shaSize} -key $keyFile -subj "$subj" -out $csrFile
    expectFileType "certificate signing request" $csrFile "PEM certificate request"

    try "create user certificate <$certFile>" \
        openssl ca -batch -notext -config $caCnfFile -in $csrFile \
            -out $certFile
    expectFileType "certificate" $certFile "PEM certificate"

    maybeAddPEMMetadata $certFile
    echo "Generated user certificate <$certFile>" >> $reportFile
}

cd $certDir

# Set up extra files and directories used by openssl-ca
mkdir -p newcerts
# Don't preserve ca-index.txt between runs.  Otherwise openssl-ca will complain
# that we're trying to issue duplicate certificates.
echo -n >ca-index.txt
echo -n 00 >ca-serial.txt

# Generate two CA certificates, one for "Jedi Order" and one for "SSITH Lord"
genSelfSigned "caKey.pem" "caCert.pem" "ca.cnf" \
    "/C=US/ST=Oregon/L=Portland/O=Galois Inc./OU=Besspin/CN=Jedi Order CA"
genSelfSigned "caKeySSITH.pem" "caCertSSITH.pem" "caSSITH.cnf" \
    "/C=US/ST=Oregon/L=Portland/O=Galois Inc./OU=Besspin/CN=SSITH Lord CA"

# Generate server and client certificates for Jedi Order
genUserCert "serverKey.pem" "serverCert.pem" "ca.cnf"\
    "/C=US/ST=Oregon/L=Portland/O=Galois Inc./OU=Besspin/CN=Jedi Order SERV"
genUserCert "clientKey.pem" "clientCert.pem" "ca.cnf"\
    "/C=US/ST=Oregon/L=Portland/O=Galois Inc./OU=Besspin/CN=Jedi Order CLNT"
genUserCert "client2Key.pem" "client2Cert.pem" "ca.cnf"\
    "/C=US/ST=Oregon/L=Portland/O=Galois Inc./OU=Besspin/CN=Yoda"

# Generate client certificates for SSITH Lord
genUserCert "clientKeySSITH.pem" "clientCertSSITH.pem" "caSSITH.cnf"\
    "/C=US/ST=Oregon/L=Portland/O=Galois Inc./OU=Besspin/CN=SSITH Lord CLNT"

# Generate a DH public parameters -- has to be DER, but -outform does not work properly with genpkey
try "create the DH public parameters <dhParams.pem>" \
        openssl genpkey -genparam -algorithm DH -pkeyopt dh_paramgen_prime_len:$dhSize -out dhParams.pem
    expectFileType "DH parameters (PEM)" dhParams.pem "ASCII text"
try "convert the DH public parameters <dhParams.pem> to DER format" \
        openssl dhparam -in dhParams.pem -inform PEM -out dhParams.der -outform DER
    expectFileType "DH parameters (DER)" dhParams.der "data"

# ------------------------ Convert the der/pem files to C header files -----------------------------
if [ "$pemORder" == 'der' ]; then
	# --------------------- Convert the pem file to der format  -----------------------------------
	openssl x509 -in caCert.pem -inform PEM -out caCert.der -outform DER &>> $reportFile
	isError $? "Error in $fileName: Failed to convert <caCert.pem> to <caCert.der>."
	openssl x509 -in caCertSSITH.pem -inform PEM -out caCertSSITH.der -outform DER &>> $reportFile
	isError $? "Error in $fileName: Failed to convert <caCertSSITH.pem> to <caCertSSITH.der>."  
	openssl x509 -in serverCert.pem -inform PEM -out serverCert.der -outform DER &>> $reportFile
	isError $? "Error in $fileName: Failed to convert <serverCert.pem> to <serverCert.der>." 
	openssl rsa -in serverKey.pem -outform DER -out serverKey.der &>> $reportFile
	isError $? "Error in $fileName: Failed to convert <serverKey.pem> to <serverKey.der>." 
	openssl x509 -in clientCert.pem -inform PEM -out clientCert.der -outform DER &>> $reportFile
	isError $? "Error in $fileName: Failed to convert <clientCert.pem> to <clientCert.der>." 
	openssl rsa -in clientKey.pem -outform DER -out clientKey.der &>> $reportFile
	isError $? "Error in $fileName: Failed to convert <clientKey.pem> to <clientKey.der>." 
	openssl x509 -in clientCertSSITH.pem -inform PEM -out clientCertSSITH.der -outform DER &>> $reportFile
	isError $? "Error in $fileName: Failed to convert <clientCertSSITH.pem> to <clientCertSSITH.der>." 
	openssl rsa -in clientKeySSITH.pem -outform DER -out clientKeySSITH.der &>> $reportFile
	isError $? "Error in $fileName: Failed to convert <clientKeySSITH.pem> to <clientKeySSITH.der>."
fi

for xFile in caCert caCertSSITH serverCert serverKey clientCert clientKey client2Cert client2Key clientCertSSITH clientKeySSITH dhParams; do
	if [[ $xFile == "dhParams" ]]; then
        xxd -i ${xFile}.der > ${xFile}.h 2>> $reportFile
    else
        xxd -i ${xFile}.${pemORder} > ${xFile}.h 2>> $reportFile
    fi
	isError $? "Error in $fileName: Failed to extract <${xFile}.${pamORder}> to <${xFile}.h>."
	sed -i "s/unsigned/static const unsigned/g" ${xFile}.h 2>> $reportFile
	isError $? "Error in $fileName: Failed to edit <${xFile}.h>."
done

# ---------- clean-up and return to previous directory
if [ "$pemORder" == 'der' ]; then rm *.der; fi
cd - &>> $reportFile

