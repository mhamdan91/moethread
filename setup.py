from setuptools import setup, find_packages
import os

VERSION = '1.1.0'
DESCRIPTION = 'Python wrapper for ThreadPoolExecutor to easily multithread resource bound tasks'
LONG_DESCRIPTION = open('README.md').read()
# Setting up
setup(
    name="moethread",
    version=VERSION,
    author="mhamdan91 (Hamdan, Muhammad)",
    author_email="<mhamdan-91@hotmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'multithreading', 'wrappers', 'decorator', 'pool', 'multitasking',
              'easy multithreading', 'thread', 'parallel', 'concurrent'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ]
)