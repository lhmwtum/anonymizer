#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name="uai-anonymizer",
    version="0.0.0",
    packages=find_packages(exclude=["test", "test.*"]),
    dependency_links=[],
)
