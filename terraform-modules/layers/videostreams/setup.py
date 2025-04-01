from setuptools import find_packages, setup

setup(
    name='videostreams',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    version='0.1.0',
    description='Videostreams library for Kinesis Video',
    author='Jedrzej Frankowski',
    license='MIT',
)
