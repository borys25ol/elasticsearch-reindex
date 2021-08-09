"""
Setup the package.
"""
from setuptools import find_packages, setup

DESCRIPTION = (
    "Python package for simple migration elasticsearch indexes between servers."
)

with open("README.md", "r") as read_me:
    long_description = read_me.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    version="0.1.0",
    name="elasticsearch-reindex",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/borys25ol/elasticsearch-reindex",
    license="MIT",
    entry_points="""
       [console_scripts]
       elasticsearch_reindex=elasticsearch_reindex.__main__:main
    """,
    author="Borys Oliinyk",
    author_email="oleynik.boris@gmail.com",
    packages=find_packages(),
    install_requires=required,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
)
