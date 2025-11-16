#!/bin/bash

# CoreMon Installer Build Script
# This script builds universal Debian packages and places them in the installer directory

set -e

# Get version from setup.py
VERSION=$(grep "version=" setup.py | sed "s/.*version=['\"]\([^'\"]*\)['\"].*/\1/")

echo "Building CoreMon universal Debian package (version $VERSION)..."

# Create installer directory if it doesn't exist
mkdir -p installer

# Clean up any existing build artifacts in parent directory
echo "Cleaning up existing build artifacts..."
rm -f ../coremon_*.deb ../coremon_*.changes ../coremon_*.buildinfo ../coremon_*.dsc ../coremon_*.tar.gz

# Temporarily modify debian/control to force universal architecture
echo "Configuring for universal architecture..."
cp debian/control debian/control.backup
sed -i 's/Architecture: any/Architecture: all/' debian/control

# Build the Debian package
echo "Building universal Debian package..."
dpkg-buildpackage -us -uc

# Restore original debian/control
mv -f debian/control.backup debian/control

# Move and rename the universal package
echo "Moving and renaming universal package..."
if ls ../coremon_*_all.deb 1> /dev/null 2>&1; then
    mv -f ../coremon_*_all.deb "installer/coremon_1.0.2-1_x64_arm64.deb"
fi

# Move other artifacts with original names
mv -f ../coremon_*.changes installer/ 2>/dev/null || true
mv -f ../coremon_*.buildinfo installer/ 2>/dev/null || true
mv -f ../coremon_*.dsc installer/ 2>/dev/null || true
mv -f ../coremon_*.tar.gz installer/ 2>/dev/null || true

echo "Build complete! Universal installer file is in the installer/ directory:"
ls -la installer/

echo ""
echo "To install locally, run: sudo apt install ./installer/coremon_1.0.2-1_x64_arm64.deb"
