"""
AWS WorkGroup
"""
import time
import os
import functools
import subprocess
import re
import shlex
import multiprocessing.pool as mpool

import paramiko

from .aws_manage import *


def subprocess_check_output(command=""):
    """convenience to run command and return its output"""
    proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    out = proc.stdout.read()
    return out


class AWSCredentials:
    """Obtain, Set and Get AWS Credentials for AWSPowerUserAccess"""

    @staticmethod
    def has_env_vars():
        """checks if necessary enviroment variables exist for from_env_vars classmethod"""
        vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
        for v in vars:
            assert v in os.environ, f"AWSCredentials must have environment variable {v} for from_env_vars " \
                                    f"classmethod"

    @staticmethod
    def has_credential_file(filename=''):
        """checks if suitable file exists for from_credentials_file classmethod"""
        # TODO: implement has_credential_file
        raise NotImplementedError

    @classmethod
    def from_env_vars(cls):
        """get AWS credentials from environment variables"""
        vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
        cls.has_env_vars()
        return cls([os.environ[v] for v in vars])

    @classmethod
    def from_credentials_file(self, filepath):
        """get AWS credentials from file"""
        # TODO: Implement from_credential_files
        raise NotImplementedError

    @classmethod
    def from_interactive(cls):
        """get AWS credentials from interactive sessions"""
        logging.info(
            f"{cls.__class__.__name__} classmethod from_interactive: performing interactive session to get AWS "
            f"credentials from the user")
        print(f"{cls.__class__.__name__} Credentials Interactive Session")
        id = input("\tEnter AWS Access Key ID: ")
        secret = input("\tEnter AWS Secret Access Key: ")
        session = input("\tEnter AWS Session Token: ")
        logging.info(f"{cls.__class__.__name__} classmethod from_interactive: finished interactive session")
        return cls([id, secret, session])

    def __init__(self, credentials):
        """store length 3 list of AWS credentials"""
        self._check_credentials(credentials)
        self._credentials = credentials
        logging.info(f"{self.__class__.__name__} successfully obtained credentials")

    def _check_credentials(self, cred):
        """ensure that the credentials are valid"""
        # credentials must be an array of length 3
        assert len(cred) == 3, f"credentials '{cred}' must be of length 3"
        # credentials must assume the string type
        for c in cred:
            assert isinstance(c, str), f"element of credentials '{c}' must be a string instance"

        # access key ID checks
        assert len(cred[0]) == 20, "AWS Access Key ID must be of length 20"
        assert re.fullmatch('[A-Z0-9]+', cred[0]), "AWS Access Key ID must be a combination of numbers and uppercase " \
                                                   "letters"

        # secret access key checks
        assert len(cred[1]) == 40, "AWS Secret Access Key must be of length 40"
        assert re.fullmatch('[a-zA-Z0-9+/]+', cred[0]), "AWS Secret Access key must be a combination of numbers, " \
                                                        "letters, '+', and '/' "

        # session token checks
        assert len(cred[2]) == 824, "AWS Session Token must be of length 824"
        assert re.fullmatch(
            '[a-zA-Z0-9+/]{19}[/]{10}[a-zA-Z0-9+/]{119,121}[/]{10}[a-zA-Z0-9+/]{662,664}==',
            cred[2]
        ), "AWS Session Token follows an incorrect pattern."

    def __getitem__(self, index):
        return self._credentials[index]

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, cred):
        self._check_credentials(cred)
        self._credentials = cred

    @property
    def access_key_id(self):
        return self._credentials[0]

    @property
    def secret_key_access(self):
        return self._credentials[1]

    @property
    def session_token(self):
        return self._credentials[2]


class FettDataWriter:
    """create FETT Target userdata file to define workload on AWS instances"""

    @classmethod
    def with_fett_repo(cls, credentials, branch=None, binaries_branch=None, key_path='~/.ssh/id_rsa.pub'):
        """add userdata to start with FETT Target at specific branch and binaries branch"""

        # Default branch on both
        if not (branch or binaries_branch):
            pass

        # If either branch is specified, we need to get a SSH key - best solution so far

        userdata = [
            "#!/bin/bash",
            "yum install -y git-lfs",
            "runuser -l centos -c 'sudo ssh-keyscan github.com >> ~/.ssh/known_hosts'",
            "cat >>/home/centos/.bashrc << EOL",
            f'export AWS_ACCESS_KEY_ID="{credentials[0]}"',
            f'export AWS_SECRET_ACCESS_KEY="{credentials[1]}"',
            f'export AWS_SESSION_TOKEN="{credentials[2]}"',
            "EOL",
        ]

        assert os.path.exists(os.path.expanduser(key_path)), f"key path {key_path} does not exist!"
        try:
            with open(os.path.expanduser(key_path), "r") as f:
                key = f.readlines()
                key = [x.strip() for x in key]
        except Exception:
            logging.error("FettDataWriter: Invalid Key Path")

        userdata_ssh = [
            "runuser -l centos -c 'touch /home/centos/.ssh/id_rsa'",
            "cat >/home/centos/.ssh/id_rsa <<EOL",
        ]
        userdata_ssh.extend(key + "EOL" + [
            "runuser -l centos -c 'chmod 600 /home/centos/.ssh/id_rsa'",
            "ssh-keygen -y -f /home/centos/.ssh/id_rsa > ~/.ssh/id_rsa.pub"
        ])

        userdata += userdata_ssh

        # Compose userdata contents, depending on whether path was specified.
        # Binaries branch and Target branch provided
        userdata_specific = [
            f"""runuser -l centos -c 'ssh-agent bash -c "ssh-add /home/centos/.ssh/id_rsa && 
                cd /home/centos/SSITH-FETT-Target/ && 
                cd SSITH-FETT-Binaries && 
                git stash && 
                cd .. &&
                git fetch &&\n""" + (
                f"git checkout {branch} &&\n" if branch else "") +
            """git pull && 
                git submodule update && 
                cd SSITH-FETT-Binaries &&\n""" + (
                f"git checkout {binaries_branch} &&\n" if binaries_branch else "") +
            """git-lfs pull && 
                cd .. "'"""
        ]

        userdata += userdata_specific

        return cls(userdata)

    def __init__(self, userdata):
        self._userdata = userdata

    def append_userdata(self, ul):
        """convenience to append to self._userdata"""
        if not isinstance(ul, str):
            self._userdata += ul
        else:
            self._userdata.append(ul)

    def with_indicator_file(self):
        """touch indicator_file as last step of userdata"""
        return self._userdata + [f"runuser -l centos -c 'touch {self.indicator_filepath()}'"]

    def append_file(self, dest, path):
        """add file contents of path to userdata"""
        assert os.path.exists(path)
        self.append_userdata(f"cat > {dest} << EOL")
        with open(path, 'r') as fp:
            self.append_userdata([l.strip() for l in fp.readlines()])
        self.append_userdata("EOL")

    def to_file(self, fname):
        """write userdata to a userdata file"""
        with open(fname, 'w') as fp:
            ud = self.with_indicator_file()
            fp.write('\n'.join(ud))
        logging.info(f"{self.__class__.__name__} wrote UserData to '{fname}'")

    def to_str(self):
        ud = self.with_indicator_file()
        return '\n'.join(ud)

    @staticmethod
    def indicator_filepath():
        return "/home/centos/fett_userdata_complete"


class EC2WorkGroup:
    """An EC2WorkGroup acts a collection of AWS instances that work can be queued to run

    A workgroup object is designed to perform n tasks with a maximum of m running AWS EC2 instance. If n > m, the jobs
    are queued until a resource frees up. If n < m, then only n instances are launched. The WorkGroup uses thread pooling
    to watch the work locally; these threads send logs periodically.
    """

    @staticmethod
    def terminate_instance(id, dry_run=False):
        if isinstance(id, str):
            terminate_instance(id, dry_run=dry_run)
        else:
            terminate_instance(id.id, dry_run=dry_run)

    @staticmethod
    def wait_on_userdata(jobidx, instance, key_filepath):
        """thread method for waiting on instance to send message """

        def get_log_str():
            return f"EC2WorkGroup-thread {jobidx}-instance {instance.id}:"

        # poll the messages associated with instance id and exit when done
        logging.info(f"{get_log_str()} wait until instance {instance.id} is running")

        # wait until instance has a public IP address
        instance.wait_until_running()
        instance.reload()
        ip_addr = instance.public_ip_address

        # SSH will be rejected for a short while after starting to run
        time.sleep(120)

        # announce waiting
        logging.info(f"{get_log_str()} ready with ip address {ip_addr}")
        logging.info(f"{get_log_str()} starting poll at address {ip_addr}...")
        is_alive = True
        iteration = 0

        # create a SSH client to instance and open SFTP session
        try:
            logging.info(f"{get_log_str()} setting up SFTP session to {ip_addr}...")
            client = paramiko.SSHClient()
            client.load_system_host_keys(filename=key_filepath)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip_addr, username="centos", key_filename=key_filepath)
            sftp = client.open_sftp()
            logging.info(f"{get_log_str()} SFTP session successful")
        except Exception as e:
            logging.error(f"{get_log_str()} SFTP session failed with error '{e}'")
            return

        # periodically check if indicator file is present on host machine
        while is_alive:
            try:
                logging.info(
                    f"{get_log_str()} polling with {FettDataWriter.indicator_filepath()} at iteration {iteration}...")
                iteration += 1
                filestat = sftp.stat(FettDataWriter.indicator_filepath())
                logging.info(f"{get_log_str()} indicator file {FettDataWriter.indicator_filepath()} found "
                             f"with file stat '{filestat}'")
                is_alive = False
                logging.info(f"{get_log_str()} completed!")
            except:
                pass

            # idle for 5 seconds
            time.sleep(5)

    @staticmethod
    def create_instance(ami_name, name, userdata, **kwargs):
        """thread create an instance for the WorkGroup"""
        # Start up an instance
        instance = launch_instance(ami_name,
                                   tags={'Name': name},
                                   user_data=userdata,
                                   **kwargs)
        # return instance object
        return instance

    @staticmethod
    def job_thread(jobidx, ami_id, name, userdata_path, key, **kwargs):
        """complete job end-to-end"""
        # create instance
        id = EC2WorkGroup.create_instance(ami_id, name, userdata_path, **kwargs)
        # wait until finished
        logging.info(f"job {jobidx} created instance {id.id}: waiting for userdata to finish...")
        EC2WorkGroup.wait_on_userdata(jobidx, id, key)
        logging.info(f"job {jobidx} for instance {id.id}: finished waiting, terminating...")
        # terminate instance
        EC2WorkGroup.terminate_instance(id)
        logging.info(f"job {jobidx} finished")

    def __init__(self, max_instances=5):
        """initialization by specifying maximum number of instances"""
        self._max_instances = max_instances
        self.pool = mpool.ThreadPool(processes=self._max_instances)

    def run_jobs(self, userdata_paths, ami_id, name, key, **kwargs):
        """submit n userdata_paths to process in ThreadPool"""
        args = [(uidx, ami_id, name + f"-{uidx}", ud, key) for uidx, ud in enumerate(userdata_paths)]
        self.pool.starmap(functools.partial(self.job_thread, **kwargs), args)
        self.pool.close()
        self.pool.join()
