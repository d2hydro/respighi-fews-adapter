# -*- coding: utf-8 -*-
from setuptools import setup
import pkg_resources  # part of setuptools


from respighifews import __version__

#%%
with open("README.md", encoding="utf8") as f:
    long_description = f.read()

setup(
    name="respighifews",
    version=__version__,
    description="Adapter for running RESPIGHI models from Delft-FEWS",
    long_description=long_description,
    url="https://github.com/d2hydro/respighi-fews-adapter",
    author="Daniel Tollenaar",
    author_email="daniel@d2hydro.nl",
    license="MIT",
    packages=["respighifews"],
    python_requires=">=3.6",
    install_requires=[
        "imod"
    ],
    keywords="respighi fews adapter",
)
