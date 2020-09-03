#!/usr/bin/env python

from setuptools import setup

install_requires = ["flask"]

tests_require = ["bandit", "black", "coverage-badge", "pytest", "pytest_pylint", "pytest-cov", "safety"]

extras = {
    "test": tests_require,
}

setup(
    author="Yuval Herziger",
    author_email="yuvalhrz@gmail.com",
    description="A declarative error handler for Flask applications",
    install_requires=install_requires,
    name="katch",
    packages=["katch"],
    package_dir={"katch": "katch"},
    setup_requires=["pytest-runner", "pytest-cov", "pytest-pylint"],
    test_suite="pytest",
    extras_require=extras,
    tests_require=tests_require,
    url="https://github.com/python-utils/katch",
    version="0.0.3",
)
