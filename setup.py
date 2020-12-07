#!/usr/bin/env python

"""The setup script."""

from pathlib import Path
from setuptools import setup

REQUIREMENTS = [
    "click>=7.0.0",
    "Flask>=1.0.0",
    "prometheus_client>=0.8.0",
    "pimoroni-sgp30>=0.0.2",
    "smbus2>=0.3.0",
]

SETUP_REQUIREMENTS = ["pytest-runner"]

TEST_REQUIREMENTS = Path("requirements_test.txt").read_text().splitlines()

CHANGELOG = Path("CHANGELOG.md").read_text()

long_description = f"{Path('README.md').read_text()}\n\n{CHANGELOG}"

setup(
    author_email="matej.urbas@gmail.com",
    author="Matej Urbas",
    entry_points={"console_scripts": ["sgp30-exporter = sgp30_exporter.main:main"]},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    keywords=["sgp30-exporter", "air quality", "prometheus", "exporter"],
    license="MIT license",
    long_description_content_type="text/markdown",
    long_description=long_description,
    name="sgp30-exporter",
    packages=["sgp30_exporter"],
    setup_requires=SETUP_REQUIREMENTS,
    test_suite="test",
    tests_require=TEST_REQUIREMENTS,
    url="https://github.com/urbas/sgp30-exporter",
    version="0.2.0",
)
