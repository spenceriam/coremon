# CoreMon - CPU Monitoring Tool

CoreMon is a lightweight system monitoring application for Linux that displays CPU temperature and load in real-time. It features a graphical interface with interactive plots and system tray indicators for quick monitoring.

## Features

- Real-time monitoring of CPU temperature and load
- Interactive graph showing historical data
- System tray indicators for temperature and load
- Configurable update interval
- Support for both Celsius and Fahrenheit
- Select specific CPU cores to monitor
- Option to start at login
- Option to start minimized to system tray

## Requirements

- Python 3.6 or higher
- GTK+ 3.0
- Python packages:
  - psutil
  - matplotlib
  - PyGObject

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cpumon.git
   cd cpumon
   ```

2. Install the required dependencies:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-dev python3-pip
   
   # Install Python packages
   pip3 install -r requirements.txt
   
   # Install the application
   sudo pip3 install .
   
   # Install desktop file (for application menu entry)
   sudo desktop-file-install cpumon.desktop
   ```

## Usage

### Launching the Application

You can launch CoreMon in several ways:

1. From the applications menu (search for "CoreMon")
2. From the terminal:
   ```bash
   cpumon
   ```

### Using the Interface

- The main window shows a graph of CPU temperature or load over time
- Use the "Switch to Load" button to toggle between temperature and load views
- Click the menu button in the header bar to access settings or quit the application
- When minimized, the application will show two system tray icons (temperature and load)
- Click on a system tray icon to show/hide the main window

### Settings

You can configure CoreMon through the Settings dialog:

- **Temperature Unit**: Switch between Celsius and Fahrenheit
- **Update Interval**: How often to update the readings (in seconds)
- **Start at login**: Automatically start CoreMon when you log in
- **Start minimized**: Start with the main window hidden (only system tray icons visible)
- **Monitored Cores**: Select which CPU cores to monitor

## Building a Debian Package (Optional)

If you want to create a .deb package for easier distribution:

```bash
# Install build dependencies
sudo apt-get install debhelper dh-python

# Build the package
dpkg-buildpackage -us -uc
```

The resulting .deb file will be created in the parent directory.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with Python, GTK, and matplotlib
- Icons from the GNOME icon set
