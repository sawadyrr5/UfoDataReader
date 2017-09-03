# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='UfoDataReader',
    version='0.0.1',
    description='Read XBRL from Ufo Catcher, and parse XBRL to GAAP.',
    author='sawadyrr5',
    author_email='riskreturn5@gmail.com',
    url='https://github.com/sawadyrr5/UfoDataReader',
    packages=find_packages(),
    install_requires=['python-xbrl', 'pandas', 'pandas_datareader', 'requests']
)
