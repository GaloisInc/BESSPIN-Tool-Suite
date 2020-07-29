"""
AWS WorkGroup
"""
import time
import functools
import multiprocessing.pool as mpool
import paramiko

from .aws_tools import *
from .userdata_creator import UserdataCreator


class EC2WorkGroup:
    """
    An EC2WorkGroup acts a collection of AWS instances that work can be queued to run

    A workgroup object is designed to perform n tasks with a maximum of m running AWS EC2 instance. If n > m, the jobs
    are queued until a resource frees up. If n < m, then only n instances are launched. The WorkGroup uses thread pooling
    to watch the work locally; these threads send logs periodically.
    """

    def __init__(self, max_instances=5):
        """
        Initialization by specifying maximum number of instances

        :param max_instances: Maximum number of instances that should be running at any given time, defaults to 5
        :type max_instances: int, optional

        :return: A new EC2WorkGroup instance
        :rtype: EC2WorkGroup
        """

        self._max_instances = max_instances
        self.pool = mpool.ThreadPool(processes=self._max_instances)

    @staticmethod
    def terminate_instance(id, dry_run=False):
        """
        Terminates an EC2 instance given the instance ID

        :param id: EC2 instance ID
        :type id: str, dict

        :param dry_run: Dry run, defaults to False
        :type dry_run: bool, optional
        """

        if isinstance(id, str):
            terminate_instance(id, dry_run=dry_run)
        else:
            terminate_instance(id.id, dry_run=dry_run)

    @staticmethod
    def wait_on_userdata(jobidx, instance, key_filepath):
        """
        Thread method for waiting on instance to send message

        :param jobidx: Job ID
        :type jobidx: str

        :param instance: Instance object
        :type instance: object

        :param key_filepath: Filepath to the SSH key
        :type key_filepath: str
        """

        log_str = f"EC2WorkGroup-thread {jobidx}-instance {instance.id}:"

        # poll the messages associated with instance id and exit when done
        logging.info(f"{log_str} wait until instance {instance.id} is running")

        # wait until instance has a public IP address
        instance.wait_until_running()
        instance.reload()
        ip_addr = instance.public_ip_address

        # SSH will be rejected for a short while after starting to run
        time.sleep(120)

        # announce waiting
        logging.info(f"{log_str} ready with ip address {ip_addr}")
        logging.info(f"{log_str} starting poll at address {ip_addr}...")
        is_alive = True
        iteration = 0

        # create a SSH client to instance and open SFTP session
        try:
            logging.info(f"{log_str} setting up SFTP session to {ip_addr}...")
            client = paramiko.SSHClient()
            client.load_system_host_keys(filename=key_filepath)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip_addr, username="centos", key_filename=key_filepath)
            sftp = client.open_sftp()
            logging.info(f"{log_str} SFTP session successful")
        except Exception as e:
            logging.error(f"{log_str} SFTP session failed with error '{e}'")
            return

        # periodically check if indicator file is present on host machine
        while is_alive:
            try:
                logging.info(
                    f"{log_str} polling with {UserdataCreator.indicator_filepath()} at iteration {iteration}...")
                iteration += 1
                filestat = sftp.stat(UserdataCreator.indicator_filepath())
                logging.info(f"{log_str} indicator file {UserdataCreator.indicator_filepath()} found "
                             f"with file stat '{filestat}'")
                is_alive = False
                logging.info(f"{log_str} completed!")
            except:  # TODO: address this
                pass

            # idle for 5 seconds
            time.sleep(5)

    @staticmethod
    def create_instance(ami_name, name, userdata, **kwargs):
        """
        Thread create an instance for the WorkGroup

        :param ami_name: AWS AMI ID
        :type ami_name: str

        :param name: AMI name
        :type name: str

        :param userdata: Script to be run on the instance
        :type userdata: str

        :return: The instance object
        :rtype: dict
        """

        # Start up an instance
        instance = launch_instance(ami_name,
                                   tags={'Name': name},
                                   user_data=userdata,
                                   **kwargs)
        # return instance object
        return instance

    @staticmethod
    def job_thread(jobidx, ami_id, name, userdata, key='~/.ssh/id_rsa.pub', **kwargs):
        """
        Complete job end-to-end

        :param jobidx: Job ID
        :type jobidx: int

        :param ami_id: AWS AMI ID
        :type ami_id: str

        :param name: AMI name
        :type name: str

        :param userdata: Userdata file contents
        :type userdata: str

        :param key: SSH key filepath, defaults to '~/.ssh/id_rsa.pub'
        :type key: str, optional
        """

        # create instance
        id = EC2WorkGroup.create_instance(ami_id, name, userdata, **kwargs)
        # wait until finished
        logging.info(f"job {jobidx} created instance {id.id}: waiting for userdata to finish...")
        EC2WorkGroup.wait_on_userdata(jobidx, id, key)
        logging.info(f"job {jobidx} for instance {id.id}: finished waiting, terminating...")
        # terminate instance
        EC2WorkGroup.terminate_instance(id)
        logging.info(f"job {jobidx} finished")

    def run_jobs(self, userdata_paths, ami_id, name, key='~/.ssh/id_rsa.pub', **kwargs):
        """
        Submit n userdata_paths to process in ThreadPool

        :param userdata_paths: Userdata paths
        :type userdata_paths: list

        :param ami_id: AWS AMI ID
        :type ami_id; str

        :param name: AMI name
        :type name: str

        :param key: SSH key filepath, defaults to '~/.ssh/id_rsa.pub'
        :type key: str
        """
        args = [(uidx, ami_id, name + f"-{uidx}", ud, key) for uidx, ud in enumerate(userdata_paths)]
        self.pool.starmap(functools.partial(self.job_thread, **kwargs), args)
        self.pool.close()
        self.pool.join()
