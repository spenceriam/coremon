#!/bin/bash

# CoreMon Installer Build Script
# This script builds Debian packages and places them in the installer directory

set -e

echo "Building CoreMon Debian packages..."

# Create installer directory if it doesn't exist
mkdir -p installer

# Clean up any existing build artifacts in parent directory
echo "Cleaning up existing build artifacts..."
rm -f ../coremon_*.deb ../coremon_*.changes ../coremon_*.buildinfo ../coremon_*.dsc ../coremon_*.tar.gz

# Build the Debian package
echo "Building Debian package..."
dpkg-buildpackage -us -uc

# Move all build artifacts to installer directory
echo "Moving build artifacts to installer directory..."
mv -f ../coremon_*.deb installer/ 2>/dev/null || true
mv -f ../coremon_*.changes installer/ 2>/dev/null || true
mv -f ../coremon_*.buildinfo installer/ 2>/dev/null || true
mv -f ../coremon_*.dsc installer/ 2>/dev/null || true
mv -f ../coremon_*.tar.gz installer/ 2>/dev/null || true

echo "Build complete! Installer files are in the installer/ directory:"
ls -la installer/

echo ""
echo "To install locally, run: sudo apt install ./installer/coremon_*.deb"
