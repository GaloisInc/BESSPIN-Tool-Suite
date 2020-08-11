import os
import re

from .logger import *


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
        log.info("AWSCredentials: successfully obtained credentials")

    @classmethod
    @log_assertion_fails
    def from_env_vars(cls):
        """
        Get AWS credentials from environment variables
        
        :raises AssertionError: Credentials not found in environment variables

        :return: A new AWSCredentials instance
        :rtype: AWSCredentials
        """

        variables = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]
        assert cls.has_env_vars(), (
            "AWSCredentials: Could not find your environment variables with AWS access keys.",
            "Please copy and paste option 1 from 'Command Line or Programatic Access' ",
            "in the AWS account dashboard into this terminal and try again.",
        )
        return cls([os.environ[v] for v in variables])

    @classmethod
    @log_assertion_fails
    def from_credentials_file(cls, filepath="~/.aws/credentials"):
        """
        Get AWS credentials from file

        :param filepath: Path for the AWS credentials file, defaults to '~/.aws/credentials'
        :type filepath: str, optional

        :raises AssertionError: Credentials could not be found in specified filepath

        :return: A new AWSCredentials instance
        :rtype: AWSCredentials
        """

        assert cls.has_credential_file(filepath), (
            "Credentials file doesn't exist: use 'aws configure', set "
            "your credentials in ~/.aws/credentials, or create a "
            "credentials file somewhere else "
        )

        keys = {"id": "", "secret": "", "session": ""}
        with open(filepath, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "aws_access_key_id" in line:
                    keys["id"] = line.strip().split("=")[1][1:]
                elif "aws_secret_access_key" in line:
                    keys["secret"] = line.strip().split("=")[1][1:]
                elif "aws_session_token" in line:
                    keys["session"] = line.strip().split("=")[1][1:]
        return cls([keys["id"], keys["secret"], keys["session"]])

    @classmethod
    def from_interactive(cls):
        """
        Get AWS credentials from interactive session

        :return: A new AWSCredentials instance
        :rtype: AWSCredentials
        """

        log.info(
            "AWSCredentials: class method from_interactive: performing interactive session to get AWS "
            "credentials from the user"
        )
        print("AWSCredentials: Credentials Interactive Session")
        key_id = input("\tEnter AWS Access Key ID: ")
        secret = input("\tEnter AWS Secret Access Key: ")
        session = input("\tEnter AWS Session Token: ")
        log.info(
            "AWSCredentials: class method from_interactive: finished interactive session"
        )
        return cls([key_id, secret, session])

    @staticmethod
    def has_env_vars():
        """
        Checks if necessary environment variables exist for from_env_vars class method
        
        :return: Whether env vars are present
        :rtype: Bool
        """

        variables = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]
        for v in variables:
            if v not in os.environ:
                return False
        return True

    @staticmethod
    def has_credential_file(filename):
        """
        Checks if suitable file exists for from_credentials_file class method
        
        :return: Whether credential file exists
        :rtype: Bool
        """

        return os.path.exists(filename)

    @staticmethod
    @log_assertion_fails
    def _check_credentials(cred):
        """
        Ensure that the credentials are valid. 

        :param cred: List of credentials
        :type cred: list

        :raises AssertionError (1): Must have 3 credentials in the list
        :raises AssertionError (2): All must be strings
        """

        # credentials must be an array of length 3
        assert len(cred) == 3, f"Credentials '{cred}' must be of length 3"
        # credentials must assume the string type
        for c in cred:
            assert isinstance(
                c, str
            ), f"Element of credentials '{c}' must be a string instance"

    @log_assertion_fails
    def __getitem__(self, index):
        """
        Gets a specified credential

        :param index: Index of the credential (0-2)
        :type index: int

        :return: The specified credential
        :rtype: str
        """

        assert 0 <= index <= 2, "Index must be between 0 and 2, inclusive"

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


class AWSConfig:
    aws_dir = os.path.expanduser("~/.aws")

    aws_config_filepath = os.path.join(aws_dir, "config")

    @staticmethod
    def has_config_file():
        return os.path.exists(AWSConfig.aws_dir) and os.path.exists(AWSConfig.aws_config_filepath)

    @staticmethod
    def check_write_aws_config(region="us-west-2", output="json"):

        # make the directory if not present
        if not os.path.exists(AWSConfig.aws_dir):
            os.mkdir(AWSConfig.aws_dir)

        # if file exists and has contents, warn user
        if os.path.exists(AWSConfig.aws_config_filepath) and os.path.getsize(AWSConfig.aws_config_filepath) > 0:
            log.warning(f"AWSConfig writing over non-empty file {AWSConfig.aws_config_filepath}")

        # write region and output to file
        with open(AWSConfig.aws_config_filepath, "w") as f:
            f.write(f"[default]\nregion = { region }\noutput = { output }")
