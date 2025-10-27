#!/usr/bin/env python3

import os
import sys
import shutil
from setuptools import setup, find_packages

# Create necessary directories
os.makedirs('build', exist_ok=True)
os.makedirs('dist', exist_ok=True)

# Install the package
setup(
    name="coremon",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyGObject>=3.36.0',
        'psutil>=5.7.0',
        'matplotlib>=3.3.0',
        'numpy>=1.19.0'
    ],
    entry_points={
        'console_scripts': [
            'coremon=coremon.main:main',
        ],
    },
    author="CoreMon Team",
    author_email="support@example.com",
    description="A system monitoring tool for Zorin OS and Ubuntu",
    license="GPL-3.0",
    keywords="monitoring cpu temperature load system",
    url="https://github.com/yourusername/coremon",
)

# Create desktop entry
desktop_entry = """[Desktop Entry]
Name=CoreMon
Comment=Monitor CPU temperature and load
Exec=coremon
Icon=coremon
Terminal=false
Type=Application
Categories=System;Utility;
StartupNotify=true
"""

desktop_file = os.path.expanduser('~/.local/share/applications/coremon.desktop')
with open(desktop_file, 'w') as f:
    f.write(desktop_entry)

print("CoreMon has been installed successfully!")
print("You can now launch it from your applications menu or by running 'coremon' in the terminal.")
