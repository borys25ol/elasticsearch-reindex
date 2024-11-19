"""
Set up the package.
"""

from setuptools import find_packages, setup

project_name = "elasticsearch-reindex"
package_name = "elasticsearch_reindex"

description = "Python package for simple migration elasticsearch indexes between different elasticsearch nodes."
version = "1.3.0"

with open("README.md") as read_me:
    long_description = read_me.read()

packages = [package for package in find_packages(where=".", exclude=("test*",))]

install_requires = ["click>8", "elasticsearch>7", "requests>=2.32.3"]

setup(
    name=project_name,
    version=version,
    author="Borys Oliinyk",
    author_email="oleynik.boris@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/borys25ol/elasticsearch-reindex",
    license="MIT",
    entry_points="""
       [console_scripts]
       elasticsearch_reindex=elasticsearch_reindex.__main__:reindex
       elasticsearch-reindex=elasticsearch_reindex.__main__:reindex
    """,
    packages=packages,
    package_data={package_name: ["py.typed"]},
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.10",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
