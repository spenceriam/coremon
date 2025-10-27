# CoreMon - System Monitor for Zorin OS

CoreMon is a lightweight system monitoring application designed for Zorin OS and other Ubuntu-based distributions. It provides real-time monitoring of CPU temperature and load, with a clean GTK-based interface.

## Features

- Real-time monitoring of CPU temperature and load for all cores
- Interactive graphs showing historical data
- System tray integration for monitoring when minimized
- Configurable update interval
- Temperature display in Celsius or Fahrenheit
- Option to start minimized
- Option to start at login

## Installation

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

## Building a Debian Package (Optional)

To create a .deb package for easier distribution:

```bash
sudo apt install dh-make build-essential devscripts
mkdir -p debian
cp debian/* .
dpkg-buildpackage -us -uc
```

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
