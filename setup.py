#!/usr/bin/env python

from distutils.core import setup

setup(
    name='PyUSPS_WebTools',
    version='0.1',
    description='Python interface to the webtools provided by the US Postal Service.',
    author='William M. Clifford',
    author_email='william.clifford.mit@gmail.com',
    url=''
    package_dir={ '': 'lib' },
    packages=[ 'usps_webtools' ],
)
