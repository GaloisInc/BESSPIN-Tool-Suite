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
    def from_env_vars(cls):
        """
        Get AWS credentials from environment variables
        
        :raises AssertionError: Credentials not found in environment variables

        :return: A new AWSCredentials instance
        :rtype: AWSCredentials
        """

        variables = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]
        assert cls.has_env_vars(), (
            f"AWSCredentials must have environment variable {v} for from_env_vars "
            f"class method"
        )
        return cls([os.environ[v] for v in variables])

    @classmethod
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
        """

        # credentials must be an array of length 3
        assert len(cred) == 3, f"Credentials '{cred}' must be of length 3"
        # credentials must assume the string type
        for c in cred:
            assert isinstance(
                c, str
            ), f"Element of credentials '{c}' must be a string instance"

        # access key ID checks
        assert len(cred[0]) == 20, "AWS Access Key ID must be of length 20"
        assert re.fullmatch("[A-Z0-9]+", cred[0]), (
            "AWS Access Key ID must be a combination of numbers and uppercase "
            "letters"
        )

        # secret access key checks
        assert len(cred[1]) == 40, "AWS Secret Access Key must be of length 40"
        assert re.fullmatch("[a-zA-Z0-9+/]+", cred[0]), (
            "AWS Secret Access key must be a combination of numbers, "
            "letters, '+', and '/'"
        )

        # session token checks
        assert len(cred[2]) >= 800, "AWS Session Token must be of length 800"
        # assert re.fullmatch(
        #     "[a-zA-Z0-9+/]{19}[/]{10}[a-zA-Z0-9+/]{119,121}[/]{10}[a-zA-Z0-9+/]{662,664}==",
        #     cred[2],
        # ), "AWS Session Token follows an incorrect pattern"

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
