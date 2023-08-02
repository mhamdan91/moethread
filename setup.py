import os
from setuptools import setup, find_packages
from pip._internal.network.session import PipSession
from pip._internal.req.req_file import parse_requirements
from moethread.version import __version__
VERSION = __version__
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
REQUIREMENTS = parse_requirements(os.path.join(PROJECT_DIR, 'requirements.txt'), session=PipSession())
DESCRIPTION = 'Python wrapper for ThreadPoolExecutor to easily multithread resource bound tasks'
LONG_DESCRIPTION = open('README.md').read()
# Setting up
setup(
    name="moethread",
    version=VERSION,
    author="mhamdan91 (Hamdan, Muhammad)",
    author_email="<mhamdan.dev@gmail.com>",
    url='https://github.com/mhamdan91/moethread',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[str(ir.requirement) for ir in REQUIREMENTS],
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