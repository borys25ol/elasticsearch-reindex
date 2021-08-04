"""
Setup the package.
"""
from setuptools import find_packages, setup

DESCRIPTION = (
    "Python package for simple migration elasticsearch indexes between servers."
)

with open("README.md", "r") as read_me:
    long_description = read_me.read()

setup(
    version="0.0.1",
    name="elasticsearch-reindex",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/borys25ol/elasticsearch-reindex",
    license="MIT",
    author="Borys Oliinyk",
    author_email="oleynik.boris@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ],
)
