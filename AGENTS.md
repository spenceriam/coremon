# AGENTS.md

## Project Overview
CoreMon is a system monitoring tool for Zorin OS and Ubuntu-based distributions. It provides real-time CPU temperature and load monitoring with a GTK-based interface, system tray integration, and configurable thresholds.

## Build Commands

### Development Setup
- Install dependencies: `sudo apt install python3-gi python3-gi-cairo python3-pip python3-setuptools`
- Install Python requirements: `pip3 install -r requirements.txt`
- Run locally: `python3 coremon/main.py`

### Building Debian Package
- Install build dependencies: `sudo apt install build-essential devscripts debhelper dh-python python3-all python3-setuptools`
- Update changelog: `export DEBEMAIL="your-email@example.com" && dch --distribution unstable --increment "Description of changes"`
- Build package: `dpkg-buildpackage -us -uc`
- Copy .deb to project: `cp ../coremon_*.deb .`

### Testing
- Run the application: `python3 coremon/main.py`
- Test package installation: `sudo apt install ./coremon_*.deb`
- Verify installation: `coremon` (should launch the app)

## Code Style and Conventions
- Python 3.12+ compatibility required
- Use GTK3 via PyGObject for UI components
- Follow PEP 8 style guidelines
- System monitoring uses psutil library
- Temperature sensors accessed via appropriate system files
- Graph plotting uses matplotlib with GTK integration

## Project Structure
- `coremon/` - Main application package
  - `main.py` - Primary application entry point
- `cpumon/` - CPU monitoring utilities
- `debian/` - Debian packaging configuration
- `setup.py` - Python package setup script
- `requirements.txt` - Python dependencies
- `coremon.desktop` - Desktop entry file
- `coremon.sh` - Launch script

## Packaging Notes
- Uses debhelper with Python 3 pybuild system
- Desktop file handled by debian packaging (not setup.py)
- Dependencies include GTK3, psutil, matplotlib, numpy
- Architecture: any (works on x86_64, ARM, etc.)

## Common Issues
- Ensure proper temperature sensor permissions
- GTK themes may affect appearance
- System tray requires appropriate indicator support
- Build artifacts appear in parent directory by default

## Git Workflow
- Main branch: `main`
- Commit format: Conventional commits preferred
- Always test package build before pushing changes
