"""AWS Instance UserData Creator

AWS Test Suite uses the ec2 user data to describe work to be accomplished by the launched
instances. UserDataCreator generates and writes valid userdata from a job description of
a FETT-Target job.
"""
from .aws_tools import *
from .logger import *


class UserdataCreator:
    """Create FETT Target userdata file to define workload on AWS instances"""

    def __init__(self, userdata=None):
        """
        Store userdata

        :param userdata: Userdata file to be sent to AWS instances
        :type userdata: str, list, optional

        :return: A new UserdataCreator instance
        :rtype: UserdataCreator
        """

        if userdata is None:
            userdata = []
        elif isinstance(userdata, str):
            userdata = userdata.split("\n")

        self._userdata = userdata

    @classmethod
    @log_assertion_fails
    def default(
        cls,
        credentials,
        name,
        index,
        branch=None,
        binaries_branch=None,
        key_path="~/.ssh/id_rsa",
    ):
        """
        Add userdata to start with FETT Target at specific branch and binaries branch

        :param credentials: AWS credentials.
        :type credentials: AWSCredentials

        :param name: Job name
        :type name: str

        :param index: FETT Target index
        :type index: int

        :param branch: What branch of SSITH-FETT-Target to run on AWS instances, defaults to 'master'
        :type branch: str, optional

        :param binaries_branch: What branch of SSITH-FETT-Binaries to run on AWS instances, defaults to 'master'
        :type binaries_branch: str, optional

        :param key_path: Path of the SSH public key, defaults to '~/.ssh/id_rsa.pub'
        :type key_path: str, optional

        :return: A new UserdataCreator instance
        :rtype: UserdataCreator
        """

        userdata = [
            "#!/bin/bash",
            "set -x",
            "exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1",
            "yum install -y git-lfs",
            "runuser -l centos -c 'sudo ssh-keyscan github.com >> ~/.ssh/known_hosts'",
            "runuser -l centos -c 'sudo ssh-keyscan gitlab-ext.galois.com >> ~/.ssh/known_hosts'",
            "cat >>/home/centos/.bashrc << EOL",
            f'export AWS_ACCESS_KEY_ID="{credentials.access_key_id}"',
            f'export AWS_SECRET_ACCESS_KEY="{credentials.secret_key_access}"',
            f'export AWS_SESSION_TOKEN="{credentials.session_token}"',
            "EOL",
            f"""runuser -l centos -c 'echo { branch if branch else "None" } >> ~/SSITH-FETT-Target/branches""",
            f"""runuser -l centos -c 'echo { binaries_branch if binaries_branch else "None" } >> ~/SSITH-FETT-Target/branches""",
        ]

        # If either branch is specified, we need to get a SSH key - best solution so far
        if branch or binaries_branch:

            assert os.path.exists(
                os.path.expanduser(key_path)
            ), f"key path {key_path} does not exist!"
            try:
                with open(os.path.expanduser(key_path), "r") as f:
                    key = f.readlines()
                    key = [x.strip() for x in key]
            except BaseException as e:
                log.error("UserdataCreator: Invalid Key Path")
                log.error(f"UserdataCreator: {e}")

            userdata_ssh = [
                "runuser -l centos -c 'touch /home/centos/.ssh/id_rsa'",
                "cat >/home/centos/.ssh/id_rsa <<EOL",
            ]
            userdata_ssh.extend(
                key
                + [
                    "EOL",
                    "runuser -l centos -c 'chmod 600 /home/centos/.ssh/id_rsa'",
                    "ssh-keygen -y -f /home/centos/.ssh/id_rsa > ~/.ssh/id_rsa.pub",
                ]
            )

            userdata += userdata_ssh

        # Compose userdata contents, depending on whether path was specified.
        # Binaries branch and Target branch provided
        userdata_specific = []

        if branch or binaries_branch:
            userdata_specific = [
                f"""runuser -l centos -c 'ssh-agent bash -c "ssh-add /home/centos/.ssh/id_rsa; 
                    cd /home/centos/SSITH-FETT-Target/; 
                    cd SSITH-FETT-Binaries; 
                    git stash; 
                    cd ..;
                    git fetch;\n"""
                + (f"git checkout {branch};\n" if branch else "")
                + """git pull; 
                    git submodule update; 
                    cd SSITH-FETT-Binaries;\n"""
                + (
                    f"git fetch; git checkout {binaries_branch} && git pull\n"
                    if binaries_branch
                    else ""
                )
                + """git-lfs pull; 
                    cd .. "'"""
            ]

        userdata_specific.append(
            f"""runuser -l centos -c 'cd /home/centos/SSITH-FETT-Target; 
                nix-shell --command "ci/fett-ci.py -ep AWSTesting runDevPR -job {name} -i {str(index)}"' """
        )

        userdata += userdata_specific

        userdata_specific_loggable = "\n".join(userdata_specific)
        log.debug(f"Userdata Specific: {userdata_specific_loggable}")

        return cls(userdata)

    def append(self, ul=""):
        """
        Convenience to append to self._userdata

        :param ul: Script to append to userdata, defaults to ''
        :type ul: str, list, optional
        """

        if not isinstance(ul, str):
            self._userdata += ul
        else:
            self._userdata.append(ul)

    @log_assertion_fails
    def append_file(self, dest, path):
        """
        Add file contents of path to userdata

        :param dest: Destination of file contents
        :type dest: str

        :param path: Filepath
        :type path: str
        """

        assert os.path.exists(path)
        self.append(f"cat > {dest} << EOL")
        with open(path, "r") as f:
            self.append([line.strip() for line in f.readlines()])
        self.append("EOL")

    def to_file(self, fname):
        """
        Write userdata to a userdata file

        :param fname: Filename
        :type fname: str
        """
        with open(fname, "w") as fp:
            ud = [f"runuser -l centos -c 'touch {self.indicator_filepath()}'"]
            fp.write("\n".join(ud))
        log.info(f"UserdataCreator: Wrote userdata to '{fname}'")

    @staticmethod
    def indicator_filepath():
        return "/home/centos/fett_userdata_complete"

    @property
    def userdata(self):
        """
        Userdata getter

        :return: Userdata
        :rtype: str
        """
        return "\n".join(self._userdata)
