[![Image](source/images/TNG_3boxes_DM_1920.jpg)](https://www.tng-project.org/)

# PyTNG

[![yt-project](https://img.shields.io/static/v1?label=%22works%20with%22&message=%22yt%22&color=%22blueviolet%22)](https://yt-project.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://zjuhone.github.io/cluster_generator)
![Python](https://img.shields.io/badge/Python_support-3.9+-orange.svg)
![testing](https://github.com/jzuhone/cluster_generator/actions/workflows/build-test.yml/badge.svg)
[![Coverage](https://coveralls.io/repos/github/Eliza-Diggins/cluster_generator/badge.svg?branch=master)](https://coveralls.io/github/Eliza-Diggins/cluster_generator)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

``PyTNG`` is a light-weight python library for interacting with the [Illustris / IllustrisTNG](https://www.tng-project.org/) simulation suites. ``pyTNG`` is designed to simplify API interaction and provide
easy transfer of data from the Illustris API to python and then to ``yt`` datasets for further analysis. Using ``pyTNG``, you can easily manage large queries to the API, sequential downloading, and data visualization.

``pyTNG`` is not officially affiliated with the IllustrisTNG team; all rights to simulations hosted through the Illustris system belong to the TNG science team and not to the developers of this package.


## Installation

``pyTNG`` is currently in a **pre-release** stage of development. If you'd like to use this package, you'll need to install it directly from the git repository. To do so,

```
>>> git clone https://www.github.com/WikGroup/pyTNG
```
Once the clone of the repository has been generated, navitage into the ``/pyTNG/`` module directory and run

```
>>> pip install .
```

The package will now be installed on your system.

### Providing a TNG API-key

Access to the TNG data is predicated on the use of an api-key, which the user must obtain on their own. Once you've created a TNG account and have an api-key, it can be
set in the configuration for the package using

```
>>> pytng-apikey <USER_API_KEY>
```

## Contributing to pyTNG

## Code of Conduct

## Licence
