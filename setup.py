#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='namecheapapi',
    version='0.2.1',
    description='Python Namecheap API wrapper',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Environment :: Web Environment',
        'Development Status :: 3 - Alpha',
    ],
    author='Alex Sanchez',
    author_email='alex@s1ck.org',
    license='MIT',
    packages=['namecheapapi'],
    url='https://github.com/yonjuuni/namecheapapi',
    keywords=['namecheap', 'domain', 'dns'],
    include_package_data=True,
    platforms=['any'],
)
