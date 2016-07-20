# django-bacman #

A simple library that takes a snapshot of a Postgres or MySQL database and uploads it to AWS S3.

## Installation ##

**Step 1:** - Install it

```bash
pip install bacman
```

**Step 2:** Add proper environment variables in your `/etc/environment` or `.pam_environment`

```bash
DATABASE_URL="postgres://dbuser:dbpass@localhost:5432/dbname"

AWS_SECRET_ACCESS_KEY="YOURAWSSECRETACCESSKEYABCDEFGHIJKLMNOPQR"
AWS_ACCESS_KEY_ID="YOURAWSACCESSKEYIDAB"

BACMAN_BUCKET="bacman-example"
BACMAN_DIRECTORY="/home/bacman/backups"
```

**Step 3:** Create .py file with the contents below

```python
from bacman.postgres import Postgres

Postgres(remove_old_tmp=True)
```

## Settings ##

### DATABASE

**DATABASE_URL**

Please add the `DATABASE_URL` variable to your `/etc/environment` or `.pam_environment`

Read more at https://github.com/kennethreitz/dj-database-url


### Amazon Web Services

**AWS_ACCESS_KEY_ID**

Please add the `AWS_ACCESS_KEY_ID` variable to your `/etc/environment` or `.pam_environment`

**AWS_SECRET_ACCESS_KEY**

Please add the `AWS_SECRET_ACCESS_KEY` variable to your `/etc/environment` or `.pam_environment`


### BacMan ###

#### BACMAN_BUCKET

Please add the `BACMAN_BUCKET` variable to your `/etc/environment` or `.pam_environment`

#### BACMAN_DIRECTORY
* default: `/tmp/bacman`

#### BACMAN_PREFIX
* default (Postgres): `pgdump`
* default (MySQL): `mysqldump`


### Examples ###

```python
# /home/bacman/runbacman.py

from bacman.postgres import Postgres

def main():
  Postgres(to_s3=True, remove_old_tmp=True)

if __name__ == "__main__":
  main()
```

```bash
# Open your crontab editor by typing crontab -e

# m h  dom mon dow   command
0 */2 * * * ~/env/bin/python ~/runbacman.py >> /home/bacman/logs/crontab.log 2>&1
```