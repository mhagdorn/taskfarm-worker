from setuptools import setup, find_packages
from sphinx.setup_command import BuildDoc

name = 'taskfarm-worker'
version = '0.2'
release = '0.2.0'
author = 'Magnus Hagdorn'

setup(
    name=name,
    packages=find_packages(),
    version=release,
    include_package_data=True,
    cmdclass={'build_sphinx': BuildDoc},
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'copyright': ('setup.py', author),
            'source_dir': ('setup.py', 'docs')}},
    setup_requires=['sphinx'],
    install_requires=[
        'requests',
    ],
    extras_require={
        'docs': [
            'sphinx_rtd_theme',
        ],
        'lint': [
            'flake8>=3.5.0',
        ],
        'testing': [
            'nose2',
            'requests-mock',
            'testtools',
            'fixtures'
        ],
    },
    entry_points={
        'console_scripts': [
            'manageTF=taskfarm_worker.manage:main',
        ],
    },
    test_suite='nose2.collector.collector',
    author=author,
    description="worker module for taskfarm",
)
