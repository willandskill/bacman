# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

# Read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bacman',
    version='0.3',
    author=u'Will & Skill AB',
    author_email='info@willandskill.se',
    packages=find_packages(),
    url='https://github.com/willandskill/bacman',
    license='BSD licence, see LICENCE.txt',
    description='Easily take snapshots of Postgres and MySQL databases and upload to AWS S3.',
    keywords=['backup', 'database', 'mysql', 'postgres'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    zip_safe=False,
    install_requires=[
        "dj-database-url>=0.3.0",
        "boto>=2.38.0"
    ]
    # test_suite = "testproject.runtests.runtests",
)