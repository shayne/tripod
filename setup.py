#!/usr/bin/env python
# Installs tripod.

import os
import sys
from distutils.core import setup

def long_description():
    """Get the long description from the README"""
    return open(os.path.join(sys.path[0], 'README.rst')).read()

setup(
    author='Shayne Sweeney',
    author_email='shayne@instagram.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: '
         'GNU Library or Lesser General Public License (LGPL)'),
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Utilities',
    ],
    description='A module that samples running scripts, logging tracebacks.',
    download_url=('https://github.com/downloads/shayne/tripod/'
                  'tripod-0.1.tar.gz'),
    keywords='debug watchdog middleware traceback',
    license='GNU LGPL',
    long_description=long_description(),
    name='tripod',
    packages=['tripod'],
    url='https://github.com/shayne/tripod',
    version='0.1',
)

