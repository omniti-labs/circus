#!/usr/bin/env python
from distutils.core import setup

setup (name="Circus",
       version="0.1.0",
       description="Command line client for Circonus",
       author="Mark Harrison",
       author_email="mark@omniti.com",
       url="http://labs.omniti.com/labs/circus",
       license="ISC",
       package_dir={'': 'src'},
       packages=['circus', 'circus.module'],
       package_data={'circus': ['templates/*/*', 'data/*', 'lib/*.py']},
       scripts=['scripts/circus']
)
