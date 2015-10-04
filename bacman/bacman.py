# -*- coding: utf-8 -*-

# Setup logger
import logging
logger = logging.getLogger(__name__)

import sys
import os
import subprocess
import boto

from datetime import datetime, timedelta

from boto.s3.key import Key

import dj_database_url


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
    aws_bucket = os.environ.get('BACMAN_BUCKET', None)

    directory = os.environ.get('BACMAN_DIRECTORY', '/tmp/bacman')
    filename_prefix = os.environ.get('BACMAN_PREFIX', 'sqldump')

    conn = None
    bucket = None

    suffix = "sql"

    # How many days should we keep the files?
    days_ago = datetime.now() - timedelta(days=7)
    tmp_hours_ago = datetime.now() - timedelta(hours=1)

    def __init__(self, to_s3=False, remove_old_s3=False, remove_old_tmp=False):
        # Check if directory exists
        self.check_directory()

        # Generate file name
        path = self.generate_file_name()
        logger.info("Creating a pg_dump file in {} ...".format(path))
        path = self.create_snapshot(path)

        if to_s3:
            self.conn = boto.connect_s3(self.aws_key, self.aws_secret)
            self.bucket = self.conn.get_bucket(os.environ['BACMAN_BUCKET'])
            logger.info("Uploading file {} to S3 bucket ({}) ...".format(path, self.aws_bucket))
            self.upload_backup_file(path)
            logger.info("File upload was successful...")

        if remove_old_s3:
            logger.info("Attempting to remove old backups from bucket {} ...".format(self.aws_bucket))
            self.remove_old_s3_backups()
            logger.info("Successfully removed old backups from bucket {} ...".format(self.aws_bucket))

        if remove_old_tmp:
            logger.info("Attempting to remove old backups from {} ...".format(self.directory))
            self.remove_old_tmp_backups()
            logger.info("Successfully removed old backups from {} ...".format(self.directory))

    def generate_file_name(self):
        # Returns the path and filename of the created file
        now = datetime.now()
        filename = "{}-{}-{}.{}".format(self.filename_prefix,
                                        now.date().strftime('%Y%m%d'),
                                        now.time().strftime('%H%M%S'),
                                        self.suffix)
        return os.path.realpath(os.path.join(self.directory, filename))

    def create_dump(self, path):
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
        except Exception, e:
            # TODO: Send mail to alert settings.admin
            raise e

    def upload_backup_file(self, path):
        conn = boto.connect_s3(self.aws_key, self.aws_secret)
        bucket = conn.get_bucket(self.aws_bucket)
        k = Key(bucket)
        # Set key to filename only
        k.key = path.split('/')[-1]
        k.set_contents_from_filename(path)

    def remove_old_s3_backups(self):
        # Delete files older than a certain period from bucket.
        for key in self.bucket.list():
            timestamp = datetime.strptime(key.last_modified, '%Y-%m-%dT%H:%M:%S.%fZ')
            if timestamp < self.days_ago:
                logger.info("Deleting file {} from S3 bucket...".format(key))
                self.bucket.delete_key(key)

    def remove_old_tmp_backups(self):
        # Delete files from local folder
        for _file in os.listdir(self.directory):
            if _file.startswith(self.filename_prefix):
                path = "{}{}".format(self.directory, _file)
                if os.path.exists(path):
                    t = os.path.getmtime(path)
                    timestamp = datetime.fromtimestamp(t)
                    if timestamp < self.tmp_hours_ago:
                        logger.info("Deleting file {} from ".format(path))
                        os.remove(path)

        logger.info('Removed old backups from directory {}...'.format(self.directory))