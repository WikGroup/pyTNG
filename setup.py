#!/usr/bin/env python
from setuptools import setup

setup(
    name="pyTNG",
    packages=["pyTNG"],
    version="0.0.1",
    description="",
    author="Eliza C. Diggins",
    author_email="eliza.diggins@utah.edu",
    url="https://github.com/Wik-Group/pyTNG",
    download_url="https://github.com/Wik-Group/pyTNG/tarball/0.1.0",
    install_requires=[
        "numpy",
        "scipy",
        "yt",
        "unyt",
        "cython",
        "ruamel.yaml",
        "dill",
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    include_package_data=True,
    scripts=["scripts/pytng-build-sh-db", "scripts/pytng-apikey"],
)
