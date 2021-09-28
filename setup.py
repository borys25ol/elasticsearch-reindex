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
    version="1.1.1",
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
    install_requires=["elasticsearch>=7.13.4", "requests>=2.26.0"],
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
)
