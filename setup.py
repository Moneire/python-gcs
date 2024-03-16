from setuptools import setup

setup(
    name='python-gcs',
    version='0.1.0',
    url='https://github.com/Moneire/python-gcs',
    author='Monere',
    author_email='ilyastep03@gmail.com',
    description='A simple Python module for interfacing with the GCS (https://armgs.team/) server.',
    package_dir={
        "": "src",
        "gcs": "src/gcs",
        "gcs.connector": "src/gcs/connector"
    },
    packages=['gcs', 'gcs.connector'],
    install_requires=[
        'requests >= 2.25.1',
        'keyring >= 23.0.1'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
