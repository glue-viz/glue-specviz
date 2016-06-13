#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
glue_specviz=glue_specviz:setup
"""

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md') as infile:
        LONG_DESCRIPTION = infile.read()

with open('glue_specviz/version.py') as infile:
    exec(infile.read())

setup(name='glue-specviz',
      version=__version__,
      description='Glue plugin for the STScI specviz tool',
      long_description=LONG_DESCRIPTION,
      url="https://github.com/glue-viz/glue-specviz",
      author='',
      author_email='',
      packages = find_packages(),
      package_data={'glue_specviz': ['*.ui']},
      entry_points=entry_points
    )
