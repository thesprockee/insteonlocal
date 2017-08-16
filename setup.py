#!/usr/bin/env python3
from setuptools import setup


setup(
    name='insteonlocal',
    py_modules=['insteonlocal'],
    version='0.53',
    description=('InsteonLocal allows local (non-cloud) '
                 'control of the Insteon Hub 2245-222'),
    author='Michael Long',
    author_email='mplong@gmail.com',
    url='https://github.com/phareous/insteonlocal',
    download_url='https://github.com/phareous/insteonlocal/tarball/0.53',
    keywords=['insteon'],
    package_data={'': ['data/*.json']},
    requires=['requests'],
    provides=['insteonlocal'],
    install_requires=[],
    packages=['insteonlocal'],
    include_package_data=True,  # use MANIFEST.in during install
    zip_safe=False,
)
