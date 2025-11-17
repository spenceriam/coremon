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
- Build package: `./build-installer.sh` (builds and places packages in installer/ directory)
- Alternative manual build: `dpkg-buildpackage -us -uc` (outputs to parent directory)

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

## Current Issues (November 2025)

### Critical Issue: Settings Not Persisting
**Status: NOT WORKING - CRITICAL**
- **Problem**: Configuration changes made in the UI are not being saved to the config file
- **Symptoms**: 
  - When users toggle "Start minimized" or "Start on login" settings, they revert to defaults after restart
  - Configuration file at `~/.config/coremon/config.ini` remains unchanged
  - Autostart desktop file is not created when "Start on login" is enabled
- **Root Cause**: Unknown - `on_setting_changed` handler is connected but settings are not persisting
- **Debug Status**: No error messages shown in console when settings are changed

### Recently Fixed: Autostart Cleanup During Uninstall
**Status: WORKING**
- **Fixed**: prerm script now properly detects user and cleans up configuration files during uninstall
- **Files Modified**: 
  - `debian/coremon.prerm` - Added proper user detection logic
  - `prerm` - Fixed file paths to use actual user directory instead of $HOME
- **Verified**: Autostart desktop file and config directory are properly removed during package uninstall

### Testing Status
- Installation: ✅ Working
- Application Launch: ✅ Working  
- Default Config Creation: ✅ Working
- Settings Persistence: ❌ NOT WORKING
- Autostart Creation: ❌ NOT WORKING
- Autostart Cleanup: ✅ Working

## Versioning Process
When making a new release:

1. **Update version in setup.py**: Change the version string
2. **Update application version**: 
   - Update `__version__` variable in `coremon/main.py`
   - Update About screen version display in `coremon/main.py` (search for "CoreMon vX.X.X")
3. **Update Debian changelog**: Use `dch --distribution unstable --increment "Description"`
4. **Build packages**: Run `./build-installer.sh` (creates universal installer in installer/ directory)
5. **Test installation**: Verify universal installer works and version displays correctly in About screen

**Important**: Always keep version numbers synchronized across:
- `setup.py` (Python package version)
- `coremon/main.py` `__version__` variable
- `coremon/main.py` About screen display
- `debian/changelog` (Debian package version)

## Git Workflow
- Main branch: `main`
- Commit format: Conventional commits preferred
- Always test package build before pushing changes
