# -*- coding: utf-8 -*-

# Setup logger
import logging
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

import boto
import dj_database_url
import os
import subprocess

from datetime import datetime, timedelta

from boto.s3.key import Key

from .utils import is_positive_number


class BacMan:
    """ Base class with some common functionality for taking database snapshots """

    url = dj_database_url.parse(os.environ['DATABASE_URL'])

    user = url['USER']
    password = url['PASSWORD']
    name = url['NAME']
    host = url['HOST']
    port = url['PORT']

    aws_key = os.environ.get('AWS_ACCESS_KEY_ID', None)
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
    bacman_bucket = os.environ.get('BACMAN_BUCKET', None)
    bacman_region = os.environ.get('BACMAN_REGION', 'eu-west-1')

    directory = os.environ.get('BACMAN_DIRECTORY', '/tmp/bacman')
    filename_prefix = os.environ.get('BACMAN_PREFIX', 'sqldump')

    conn = None
    bucket = None

    suffix = "sql"

    def __init__(self, to_remote=False, cleanup_remote_snapshots=False, cleanup_local_snapshots=False,
                 remote_snapshot_timeout=None, local_snapshot_timeout=None):

        # 1. Check that proper directory exists in file system
        # 2. Generate filename for snapshot
        # 3. Take snapshot of database
        # 4. Set timeout value in hours for remote snapshot, if invalid or None, use the default of 720 hours = 30 days
        # 5. Set timeout value in hours for local snapshot, if invalid or None, use the default of 720 hours = 30 days
        # 6. If 'to_remote' is True, try to connect to remote storage and upload newly created snapshot
        # 7. If 'cleanup_remote_snapshots' is True, try to connect to remote storage and remove outdated snapshots
        # 8. If 'cleanup_local_snapshots' is True, try to remove outdated snapshots from local file system

        # Check if directory exists
        self.check_directory()

        # Generate file name
        path = self.generate_file_name()
        logger.info("Creating a pg_dump file in {} ...".format(path))
        path = self.create_snapshot(path)

        if cleanup_remote_snapshots:
            # How many hours should we keep the files in our S3 bucket?
            self.remote_snapshot_timeout = datetime.now() - timedelta(hours=720)
            if remote_snapshot_timeout is not None:
                if is_positive_number(remote_snapshot_timeout):
                    self.remote_snapshot_timeout = datetime.now() - timedelta(hours=remote_snapshot_timeout)
                else:
                    message = "Invalid parameter passed for 'remote_snapshot_timeout'. Using default: {} hours!".format(
                        self.remote_snapshot_timeout
                    )
                    logger.info(message)

        if cleanup_local_snapshots:
            # How many hours should we keep the files in our local filesystem?
            self.local_snapshot_timeout = datetime.now() - timedelta(hours=720)
            if local_snapshot_timeout is not None:
                if is_positive_number(local_snapshot_timeout):
                    self.local_snapshot_timeout = datetime.now() - timedelta(hours=local_snapshot_timeout)
                else:
                    message = "Invalid parameter passed for 'local_snapshot_timeout'. Using default: {} hours!".format(
                        self.local_snapshot_timeout
                    )
                    logger.info(message)

        if to_remote:
            # Check that valid aws_key and aws_secret is set
            if self.aws_key is not None and self.aws_secret is not None:
                self.conn = boto.s3.connect_to_region(
                    self.bacman_region,
                    aws_access_key_id=self.aws_key,
                    aws_secret_access_key=self.aws_secret,
                    is_secure=True)

            self.bucket = self.conn.get_bucket(self.bacman_bucket)
            logger.info("Uploading file {} to S3 bucket ({}) ...".format(path, self.bacman_bucket))
            self.upload_snapshot(path)
            logger.info("File upload was successful...")

        if cleanup_remote_snapshots:
            logger.info("Attempting to remove old backups from bucket {} ...".format(self.bacman_bucket))
            self.remove_outdated_remote_snapshots()
            logger.info("Successfully removed old backups from bucket {} ...".format(self.bacman_bucket))

        if cleanup_local_snapshots:
            logger.info("Attempting to remove old backups from {} ...".format(self.directory))
            self.remove_outdated_local_snapshots()
            logger.info("Successfully removed old backups from {} ...".format(self.directory))

    def generate_file_name(self):
        # Returns the path and filename of the created file
        now = datetime.now()
        filename = "{}-{}-{}.{}".format(self.filename_prefix,
                                        now.date().strftime('%Y%m%d'),
                                        now.time().strftime('%H%M%S'),
                                        self.suffix)
        return os.path.realpath(os.path.join(self.directory, filename))

    def get_command(self, path):
        raise NotImplementedError("Please implement this function in a subclass!")

    def check_directory(self):
        # Check if path exists
        if not os.path.exists(self.directory):
            logger.info("Creating directory {} ...".format(self.directory))
            os.makedirs(self.directory)

    def create_snapshot(self, path):
        try:
            subprocess.call(self.get_command(path), shell=True)
            return path
        except Exception as e:
            # TODO: Send mail to alert settings.admin
            logger.exception(e)
            raise e

    def upload_snapshot(self, path):
        k = Key(self.bucket)
        # Set key to filename only
        k.key = path.split('/')[-1]
        k.set_contents_from_filename(path)

    def remove_outdated_remote_snapshots(self):
        # Delete files older than a certain period from bucket.
        for key in self.bucket.list():
            timestamp = datetime.strptime(key.last_modified, '%Y-%m-%dT%H:%M:%S.%fZ')
            logger.info("Checking remote file {} with <Timestamp: {}>...".format(key, timestamp))
            if timestamp < self.remote_snapshot_timeout:
                logger.info("Deleting file <{}> from remote storage...".format(key))
                self.bucket.delete_key(key)

    def remove_outdated_local_snapshots(self):
        # Delete files from local folder
        for _file in os.listdir(self.directory):
            if _file.startswith(self.filename_prefix):
                path = os.path.realpath(os.path.join(self.directory, _file))
                if os.path.exists(path):
                    t = os.path.getmtime(path)
                    timestamp = datetime.fromtimestamp(t)
                    if timestamp < self.local_snapshot_timeout:
                        logger.info("Deleting file <{}> from local file system...".format(path))
                        os.remove(path)

        logger.info('Removed outdated snapshots from directory {}...'.format(self.directory))
