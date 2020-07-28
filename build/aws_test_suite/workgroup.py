"""
AWS WorkGroup
"""
import time
import functools
import multiprocessing.pool as mpool
import paramiko

from .aws_tools import *


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
