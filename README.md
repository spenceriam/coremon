# CoreMon - System Monitor for Zorin OS

CoreMon is a lightweight system monitoring application designed for Zorin OS and other Ubuntu-based distributions. It provides real-time monitoring of CPU temperature and load, with a clean GTK-based interface.

## Features

### Core Monitoring
- **Real-time CPU Temperature Monitoring**: Monitor temperature for individual CPU cores or system average
- **CPU Load Monitoring**: Track CPU usage percentage across all cores
- **Historical Data Visualization**: Interactive graphs showing temperature and load trends over time
- **Configurable Update Intervals**: Adjust monitoring frequency from 1-10 seconds

### User Interface
- **Clean GTK3 Interface**: Modern, responsive design using GTK3 framework
- **System Tray Integration**: Minimize to system tray with continuous monitoring
- **Dashboard View**: At-a-glance view of current system metrics
- **Settings Panel**: Comprehensive configuration options
- **Temperature Unit Support**: Switch between Celsius and Fahrenheit

### System Integration
- **Desktop Entry**: Launch from applications menu with proper icon integration
- **Auto-start Option**: Configure to start automatically at login
- **Start Minimized**: Option to launch directly to system tray
- **Configuration Persistence**: Settings saved in `~/.config/coremon/`

### Advanced Features
- **Threshold Alerts**: Visual indicators when temperature or load exceeds configurable thresholds
- **Individual Core Monitoring**: Toggle between average view and per-core monitoring
- **Smooth Graph Rendering**: Optional smoothing for better visualization
- **Window State Management**: Remembers window size and position

## Installation

### Option 1: Debian Package (Recommended)
Download and install the pre-built .deb package:

```bash
sudo apt install ./coremon_1.0.0-1.2_amd64.deb
```

### Option 2: From Source

1. Install the required dependencies:

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo python3-pip python3-setuptools
pip3 install -r requirements.txt
```

2. Install CoreMon:

```bash
sudo python3 setup.py install
```

3. Launch CoreMon from your applications menu or by running `coremon` in the terminal.

## Usage

- The main window shows current CPU temperature and load, along with historical graphs.
- Use the Settings tab to configure update intervals, temperature units, and startup behavior.
- When minimized, CoreMon will show temperature and load in the system tray.
- To close the application, right-click the system tray icon and select "Quit".

## Building a Debian Package

To create a .deb package for easier distribution:

```bash
# Install build dependencies
sudo apt install build-essential devscripts debhelper dh-python python3-all python3-setuptools

# Update changelog (optional)
export DEBEMAIL="your-email@example.com"
dch --distribution unstable --increment "Description of changes"

# Build package
dpkg-buildpackage -us -uc

# Copy .deb to project directory
cp ../coremon_*.deb .
```

## System Requirements

### Supported Distributions
- Zorin OS 16+ 
- Ubuntu 20.04+
- Other Ubuntu-based distributions

### Dependencies
- Python 3.8+
- GTK3 3.36+
- PyGObject 3.36+
- psutil 5.7+
- matplotlib 3.3+
- numpy 1.19+

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
