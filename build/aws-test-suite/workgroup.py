"""
AWS WorkGroup
"""
import time
import os
import functools
import re
import multiprocessing.pool as mpool

import paramiko

from .aws_manage import *


class AWSCredentials:
    """Obtain, set and get AWS credentials for AWSPowerUserAccess."""

    def __init__(self, credentials):
        """
        Store length 3 list of AWS credentials

        :param credentials: List of AWS credentials: AWS Access Key ID, AWS Secret Access Key, and AWS Session Token
        :type credentials: list

        :return: A new AWSCredentials instance
        :rtype: AWSCredentials
        """

        self._check_credentials(credentials)
        self._credentials = credentials
        logging.info(f"{self.__class__.__name__} successfully obtained credentials")

    @classmethod
    def from_env_vars(cls):
        """
        Get AWS credentials from environment variables

        :return: A new AWSCredentials instance
        :rtype: AWSCredentials
        """

        vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
        cls.has_env_vars()
        return cls([os.environ[v] for v in vars])

    @classmethod
    def from_credentials_file(cls, filepath='~/.aws/credentials'):
        """
        Get AWS credentials from file

        :param filepath: (Optional) Path for the AWS credentials file, defaults to '~/.aws/credentials'
        :type filepath: str, optional

        :return: A new AWSCredentials instance
        :rtype: AWSCredentials
        """

        cls.has_credential_file(filepath)

        keys = {id: '', secret: '', session: ''}
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for l in lines:
                if 'aws_access_key_id' in l:
                    keys['id'] = l.strip().split('=')[1][1:]
                elif 'aws_secret_access_key' in l:
                    keys['secret'] = l.strip().split('=')[1][1:]
                elif 'aws_session_token' in l:
                    keys['session'] = l.strip().split('=')[1][1:]
        return cls([keys.id, keys.secret, keys.session])

    @classmethod
    def from_interactive(cls):
        """
        Get AWS credentials from interactive session

        :return: A new AWSCredentials instance
        :rtype: AWSCredentials
        """

        logging.info(
            f"{cls.__class__.__name__} classmethod from_interactive: performing interactive session to get AWS "
            f"credentials from the user")
        print(f"{cls.__class__.__name__} Credentials Interactive Session")
        id = input("\tEnter AWS Access Key ID: ")
        secret = input("\tEnter AWS Secret Access Key: ")
        session = input("\tEnter AWS Session Token: ")
        logging.info(f"{cls.__class__.__name__} classmethod from_interactive: finished interactive session")
        return cls([id, secret, session])

    @staticmethod
    def has_env_vars():
        """
        Checks if necessary environment variables exist for from_env_vars classmethod

        :raises AssertionError: Credentials not found in environment variables
        """

        vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
        for v in vars:
            assert v in os.environ, f"AWSCredentials must have environment variable {v} for from_env_vars " \
                                    f"classmethod"

    @staticmethod
    def has_credential_file(filename):
        """
        Checks if suitable file exists for from_credentials_file classmethod

        :raises AssertionError: Credentials could not be found in specified filepath
        """

        assert os.path.exists(filename), "Credentials file doesn't exist: use 'aws configure', set " \
                                         "your credentials in ~/.aws/credentials, or create a " \
                                         "credentials file somewhere else "

    @staticmethod
    def _check_credentials(cred):
        """
        Ensure that the credentials are valid

        :param cred: List of credentials
        :type cred: list

        :raises AssertionError (1): Must have 3 credentials in the list
        :raises AssertionError (2): First key must be length 20 (AWS Access Key ID)
        :raises AssertionError (3): First key must conform to key pattern (AWS Access Key ID)
        :raises AssertionError (4): Second key must be length 40 (AWS Secret Access Key)
        :raises AssertionError (5): Second key must conform to key pattern (AWS Secret Access Key)
        :raises AssertionError (6): Third key must be length 846 (AWS Session Token)
        :raises AssertionError (7): Third key must conform to key pattern (AWS Session Token)
        """

        # credentials must be an array of length 3
        assert len(cred) == 3, f"Credentials '{cred}' must be of length 3"
        # credentials must assume the string type
        for c in cred:
            assert isinstance(c, str), f"Element of credentials '{c}' must be a string instance"

        # access key ID checks
        assert len(cred[0]) == 20, "AWS Access Key ID must be of length 20"
        assert re.fullmatch('[A-Z0-9]+', cred[0]), "AWS Access Key ID must be a combination of numbers and uppercase " \
                                                   "letters"

        # secret access key checks
        assert len(cred[1]) == 40, "AWS Secret Access Key must be of length 40"
        assert re.fullmatch('[a-zA-Z0-9+/]+', cred[0]), "AWS Secret Access key must be a combination of numbers, " \
                                                        "letters, '+', and '/'"

        # session token checks
        assert len(cred[2]) == 824, "AWS Session Token must be of length 824"
        assert re.fullmatch(
            '[a-zA-Z0-9+/]{19}[/]{10}[a-zA-Z0-9+/]{119,121}[/]{10}[a-zA-Z0-9+/]{662,664}==',
            cred[2]
        ), "AWS Session Token follows an incorrect pattern"

    def __getitem__(self, index):
        """
        Gets a specified credential

        :param index: Index of the credential (0-2)
        :type index: int

        :return: The specified credential
        :rtype: str
        """

        assert 0 < index < 2, "Index must be between 0 and 2, inclusive"

        return self._credentials[index]

    @property
    def credentials(self):
        """
        Getter for the 'credentials' property. Returns the list of credentials.

        :return: The list of credentials
        :rtype: list
        """

        return self._credentials

    @credentials.setter
    def credentials(self, cred):
        """
        Setter for the 'credentials' property.

        :param cred: List of credentials
        :type cred: list
        """
        self._check_credentials(cred)
        self._credentials = cred

    @property
    def access_key_id(self):
        """
        Getter for the AWS Access Key ID.

        :return: AWS Access Key ID
        :rtype: str
        """
        return self.__getitem__(0)

    @property
    def secret_key_access(self):
        """
        Getter for the AWS Secret Access Key.

        :return: AWS Secret Access Key
        :rtype: str
        """
        return self.__getitem__(1)

    @property
    def session_token(self):
        """
        Getter for the AWS Session Token.

        :return: AWS Session Token
        :rtype: str
        """
        return self.__getitem__(2)


class UserdataCreator:
    """Create FETT Target userdata file to define workload on AWS instances"""

    def __init__(self, userdata):
        """
        Store userdata

        :param userdata: Userdata file to be sent to AWS instances
        :type userdata: str

        :return: A new UserdataCreator instance
        :rtype: UserdataCreator
        """

        self._userdata = userdata

    @classmethod
    def with_fett_repo(cls, credentials, branch=None, binaries_branch=None, key_path='~/.ssh/id_rsa.pub'):
        """
        Add userdata to start with FETT Target at specific branch and binaries branch

        :param credentials: AWS credentials.
        :type credentials: AWSCredentials

        :param branch: What branch of SSITH-FETT-Target to run on AWS instances, defaults to 'master'
        :type branch: str, optional

        :param binaries_branch: What branch of SSITH-FETT-Binaries to run on AWS instances, defaults to 'master'
        :type binaries_branch: str, optional

        :param key_path: Path of the SSH public key, defaults to '~/.ssh/id_rsa.pub'
        :type key_path: str, optional

        :return: A new UserdataCreator instance
        :rtype: UserdataCreator
        """

        # Default branch on both
        if not (branch or binaries_branch):
            pass

        # If either branch is specified, we need to get a SSH key - best solution so far
        userdata = [
            "#!/bin/bash",
            "yum install -y git-lfs",
            "runuser -l centos -c 'sudo ssh-keyscan github.com >> ~/.ssh/known_hosts'",
            "cat >>/home/centos/.bashrc << EOL",
            f'export AWS_ACCESS_KEY_ID="{credentials.access_key_id}"',
            f'export AWS_SECRET_ACCESS_KEY="{credentials.secret_key_access}"',
            f'export AWS_SESSION_TOKEN="{credentials.session_token}"',
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

    def append_to_userdata(self, ul=''):
        """
        Convenience to append to self._userdata

        :param ul: Script to append to userdata, defaults to ''
        :type ul: str, list, optional
        """

        if not isinstance(ul, str):
            self._userdata += ul
        else:
            self._userdata.append(ul)

    def append_file(self, dest, path):
        """
        Add file contents of path to userdata

        :param dest: Destination of file contents
        :type dest: str

        :param path: Filepath
        :type path: str
        """

        assert os.path.exists(path)
        self.append_to_userdata(f"cat > {dest} << EOL")
        with open(path, 'r') as fp:
            self.append_to_userdata([l.strip() for l in fp.readlines()])
        self.append_to_userdata("EOL")

    def to_file(self, fname):
        """
        Write userdata to a userdata file

        :param fname: Filename
        :type fname: str
        """
        with open(fname, 'w') as fp:
            ud = [f"runuser -l centos -c 'touch {self.indicator_filepath()}'"]
            fp.write('\n'.join(ud))
        logging.info(f"{self.__class__.__name__} wrote UserData to '{fname}'")

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
