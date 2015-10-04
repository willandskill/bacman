# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

setup(
    name='bacman',
    version='0.1',
    author='Faisal Mahmud',
    author_email='faisal@willandskill.se',
    packages=find_packages(),
    url='https://github.com/willandskill/bacman',
    license='BSD licence, see LICENCE.txt',
    keywords=['backup', 'database', 'mysql', 'postgres'],
    description='Take snapshots of Postgres and MySQL databases and upload to AWS S3.',
    long_description=open('README.md').read(),
    zip_safe=False,
    # test_suite = "testproject.runtests.runtests",
)