"""
Setup the package.
"""
from setuptools import find_packages, setup

project_name = "elasticsearch-reindex"
package_name = "elasticsearch_reindex"

description = (
    "Python package for simple migration elasticsearch indexes between servers."
)
version = "1.2.0"

with open("README.md") as read_me:
    long_description = read_me.read()

packages = [package for package in find_packages(where=".", exclude=("test*",))]

install_requires = [
    "click-default-group==1.2.2",
    "elasticsearch>=7.13.4",
    "requests>=2.26.0",
]

setup(
    version=version,
    name=project_name,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/borys25ol/elasticsearch-reindex",
    license="MIT",
    entry_points="""
       [console_scripts]
       elasticsearch_reindex=elasticsearch_reindex.__main__:cli
    """,
    author="Borys Oliinyk",
    author_email="oleynik.boris@gmail.com",
    packages=packages,
    package_data={package_name: ["py.typed"]},
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
