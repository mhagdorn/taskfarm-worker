from setuptools import setup, find_packages

setup(
    name = "taskfarm-worker",
    packages = find_packages(),
    include_package_data = True,
    install_requires = [

    ],
    author = "Magnus Hagdorn",
    description = "worker module for taskfarm",
)
