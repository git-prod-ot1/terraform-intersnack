from setuptools import find_packages, setup

setup(
    name='lambda2kinesis',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    version='0.1.0',
    description='Helper library for lambda2kinesis module',
    author='Jedrzej Frankowski',
    author_email='jfrankowski@bytesmith.pl',
    license='MIT',
)
