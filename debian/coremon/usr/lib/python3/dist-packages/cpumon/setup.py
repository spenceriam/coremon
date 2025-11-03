from setuptools import setup, find_packages
import os

# Read the contents of README.md for the long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="cpumon",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'psutil>=5.7.0',
        'matplotlib>=3.3.0',
        'PyGObject>=3.36.0',
    ],
    entry_points={
        'console_scripts': [
            'cpumon=cpumon.main:main',
        ],
    },
    # Include non-Python files
    include_package_data=True,
    # Metadata
    author="Your Name",
    author_email="your.email@example.com",
    description="A system monitoring tool for CPU temperature and load",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cpumon",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    python_requires='>=3.6',
)
