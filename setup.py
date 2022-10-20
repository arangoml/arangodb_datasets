#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requirements = ["python-arango>=7.4.1", "requests>=2.28.1", "rich>=12.6.0"]


dev_requirements = [
    "bandit>=1.7.4",
    "black>=22.10.0",
    "flake8>=5.0.4",
    "isort>=5.10.1",
    "mypy>=0.982",
    "pre-commit>=2.20.0",
    "pytest>=7.1.3",
    "pytest-cov>=4.0.0",
    "sphinx>=5.3.0",
    "types-requests>=2.28.11.2",
    "types-setuptools>=65.5.0.1",
]

setup(
    name="arango_datasets",
    version="1.0.0",
    author="Chris Woodward",
    author_email="christopher@arangodb.com",
    description="Package for fetching and loading datasets for ArangoDB deployments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cw00dw0rd/arango_datasets",
    project_urls={
        "Bug Tracker": "https://github.com/cw00dw0rd/arango_datasets",
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="Apache Software License 2.0",
    keywords="arango_datasets",
    package_dir={"arango_datasets": "arango_datasets"},
    packages=find_packages(include=["arango_datasets", "arango_datasets.*"]),
    include_package_data=True,
    # -----
    install_requires=install_requirements,
    test_suite="tests",
    extras_require={"dev": dev_requirements},
    zip_safe=False,
)
