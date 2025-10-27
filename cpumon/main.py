#!/usr/bin/env python3

import gi
import os
import threading
import time
import psutil
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from gi.repository import Gtk, GLib, Gdk, Gio
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import numpy as np
import json
import os.path
from collections import deque

class CoreMonApp:
    def __init__(self):
        self.app = Gtk.Application(application_id='org.cpumon.app')
        self.app.connect('activate', self.on_activate)
        self.app.connect('shutdown', self.on_shutdown)
        
        # Default settings
        self.settings = {
            'start_minimized': False,
            'start_at_login': False,
            'temp_unit': 'C',  # 'C' or 'F'
            'update_interval': 3,  # seconds
            'max_data_points': 60,  # Number of data points to show in graph
            'monitored_cores': list(range(psutil.cpu_count()))  # Monitor all cores by default
        }
        
        self.load_settings()
        
        # Data storage
        self.timestamps = deque(maxlen=self.settings['max_data_points'])
        self.temps = {i: deque(maxlen=self.settings['max_data_points']) 
                     for i in self.settings['monitored_cores']}
        self.loads = {i: deque(maxlen=self.settings['max_data_points']) 
                     for i in self.settings['monitored_cores']}
        
        self.is_running = False
        self.thread = None
        self.window = None
        self.temp_indicator = None
        self.load_indicator = None
        self.plot_canvas = None
        self.plot_type = 'temperature'  # or 'load'
    
    def load_settings(self):
        config_dir = os.path.expanduser('~/.config/cpumon')
        config_file = os.path.join(config_dir, 'settings.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        config_dir = os.path.expanduser('~/.config/cpumon')
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, 'settings.json')
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def on_activate(self, app):
        self.create_main_window()
        
        if not self.settings['start_minimized']:
            self.window.show_all()
            self.start_monitoring()
        else:
            self.window.hide()
            self.create_indicators()
            self.start_monitoring()
    
    def create_main_window(self):
        self.window = Gtk.ApplicationWindow(application=self.app, title="CoreMon")
        self.window.set_default_size(800, 600)
        self.window.set_border_width(10)
        
        # Create main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.add(main_box)
        
        # Create header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "CoreMon"
        self.window.set_titlebar(header)
        
        # Add menu button
        menu_btn = Gtk.MenuButton()
        menu_icon = Gio.ThemedIcon(name="open-menu-symbolic")
        menu_image = Gtk.Image.new_from_gicon(menu_icon, Gtk.IconSize.BUTTON)
        menu_btn.add(menu_image)
        header.pack_end(menu_btn)
        
        # Create menu
        menu = Gtk.Menu()
        menu_btn.set_popup(menu)
        
        # Add menu items
        settings_item = Gtk.MenuItem(label="Settings")
        settings_item.connect("activate", self.show_settings_dialog)
        menu.append(settings_item)
        
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit_clicked)
        menu.append(quit_item)
        menu.show_all()
        
        # Create plot area
        self.create_plot_area(main_box)
        
        # Create status bar
        status_box = Gtk.Box(spacing=6)
        main_box.pack_end(status_box, False, False, 0)
        
        self.status_label = Gtk.Label()
        status_box.pack_start(self.status_label, True, True, 0)
        
        # Toggle button for plot type
        toggle_btn = Gtk.ToggleButton(label="Switch to Load")
        toggle_btn.connect("toggled", self.on_toggle_plot_type)
        status_box.pack_end(toggle_btn, False, False, 0)
        
        self.window.connect("delete-event", self.on_window_delete)
    
    def create_plot_area(self, parent):
        # Create a figure and axis for the plot
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create the canvas and add it to the window
        self.plot_canvas = FigureCanvas(self.fig)
        self.plot_canvas.set_size_request(600, 400)
        
        # Add some initial data
        self.ax.set_title('CPU Temperature Over Time')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Temperature (°C)')
        self.ax.grid(True)
        
        # Create lines for each core
        self.temp_lines = {}
        self.load_lines = {}
        
        for core in self.settings['monitored_cores']:
            line, = self.ax.plot([], [], label=f'Core {core}')
            self.temp_lines[core] = line
            
        self.ax.legend()
        
        # Add the canvas to the window
        parent.pack_start(self.plot_canvas, True, True, 0)
    
    def update_plot(self):
        if not self.timestamps:
            return
            
        self.ax.clear()
        
        if self.plot_type == 'temperature':
            self.ax.set_title('CPU Temperature Over Time')
            self.ax.set_ylabel(f'Temperature (°{self.settings["temp_unit"]})')
            
            for core, temps in self.temps.items():
                if temps:  # Only plot if we have data
                    if self.settings['temp_unit'] == 'F':
                        # Convert C to F if needed
                        y_data = [(temp * 9/5) + 32 for temp in temps]
                    else:
                        y_data = temps
                    
                    self.ax.plot(
                        list(self.timestamps)[-len(temps):], 
                        y_data,
                        label=f'Core {core}'
                    )
        else:  # Load
            self.ax.set_title('CPU Load Over Time')
            self.ax.set_ylabel('Load (%)')
            
            for core, loads in self.loads.items():
                if loads:  # Only plot if we have data
                    self.ax.plot(
                        list(self.timestamps)[-len(loads):], 
                        loads,
                        label=f'Core {core}'
                    )
        
        self.ax.set_xlabel('Time')
        self.ax.grid(True)
        self.ax.legend()
        
        # Rotate x-axis labels for better readability
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adjust layout to prevent label cutoff
        self.fig.tight_layout()
        
        # Redraw the canvas
        self.plot_canvas.draw_idle()
    
    def on_toggle_plot_type(self, button):
        if button.get_active():
            button.set_label("Switch to Temperature")
            self.plot_type = 'load'
        else:
            button.set_label("Switch to Load")
            self.plot_type = 'temperature'
        
        self.update_plot()
    
    def create_indicators(self):
        # Create system tray indicators
        self.temp_indicator = Gtk.StatusIcon()
        self.load_indicator = Gtk.StatusIcon()
        
        # Set initial values
        self.update_indicators(0, 0)
        
        # Connect click events
        self.temp_indicator.connect("activate", self.on_indicator_clicked)
        self.load_indicator.connect("activate", self.on_indicator_clicked)
    
    def update_indicators(self, avg_temp, avg_load):
        if self.settings['temp_unit'] == 'F':
            temp_str = f"{avg_temp*9/5 + 32:.1f}°F"
        else:
            temp_str = f"{avg_temp:.1f}°C"
            
        load_str = f"{avg_load:.1f}%"
        
        # Update tooltips
        if self.temp_indicator:
            self.temp_indicator.set_tooltip_text(f"CPU Temp: {temp_str}")
            self.temp_indicator.set_from_icon_name("temperature-high")
            
        if self.load_indicator:
            self.load_indicator.set_tooltip_text(f"CPU Load: {load_str}")
            self.load_indicator.set_from_icon_name("system-run")
    
    def on_indicator_clicked(self, widget):
        if self.window.get_visible():
            self.window.hide()
        else:
            self.window.show_all()
    
    def start_monitoring(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.thread.start()
    
    def stop_monitoring(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
    
    def monitor_loop(self):
        while self.is_running:
            try:
                # Get current timestamp
                now = datetime.now()
                self.timestamps.append(now)
                
                # Get CPU temperatures
                temps = self.get_cpu_temperature()
                
                # Get CPU loads
                loads = psutil.cpu_percent(interval=0.1, percpu=True)
                
                # Update data
                for core in self.settings['monitored_cores']:
                    if core < len(temps):
                        self.temps[core].append(temps[core])
                    if core < len(loads):
                        self.loads[core].append(loads[core])
                
                # Calculate averages for indicators
                avg_temp = sum(temps) / len(temps) if temps else 0
                avg_load = sum(loads) / len(loads) if loads else 0
                
                # Update UI in main thread
                GLib.idle_add(self.update_ui, avg_temp, avg_load)
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
            
            # Sleep for the update interval
            time.sleep(self.settings['update_interval'])
    
    def get_cpu_temperature(self):
        """Get CPU temperature for all cores."""
        temps = []
        
        # Try to get temperature from different possible locations
        temp_paths = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/class/hwmon/hwmon0/temp1_input",
            "/sys/class/hwmon/hwmon1/temp1_input"
        ]
        
        for path in temp_paths:
            try:
                with open(path, 'r') as f:
                    temp = float(f.read().strip()) / 1000.0  # Convert millidegrees to degrees
                    temps.append(temp)
            except (IOError, ValueError):
                continue
        
        # If no temperature found, try using psutil
        if not temps and hasattr(psutil, "sensors_temperatures"):
            try:
                temps_info = psutil.sensors_temperatures()
                if 'coretemp' in temps_info:
                    for entry in temps_info['coretemp']:
                        if 'Core' in entry.label:
                            temps.append(entry.current)
            except Exception:
                pass
        
        # If still no temperatures, return a dummy value
        if not temps:
            temps = [0.0] * psutil.cpu_count()
        
        return temps
    
    def update_ui(self, avg_temp, avg_load):
        # Update status label
        if self.settings['temp_unit'] == 'F':
            temp_str = f"{avg_temp*9/5 + 32:.1f}°F"
        else:
            temp_str = f"{avg_temp:.1f}°C"
            
        self.status_label.set_text(f"Avg Temp: {temp_str} | Avg Load: {avg_load:.1f}%")
        
        # Update indicators if they exist
        if self.temp_indicator and self.load_indicator:
            self.update_indicators(avg_temp, avg_load)
        
        # Update plot
        self.update_plot()
        
        return False  # Ensures this function is only run once by GLib
    
    def show_settings_dialog(self, widget=None):
        dialog = Gtk.Dialog("CoreMon Settings", self.window,
                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OK, Gtk.ResponseType.OK))
        
        dialog.set_default_size(400, 300)
        
        # Create content area
        content_area = dialog.get_content_area()
        content_area.set_spacing(6)
        
        # Create settings grid
        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(6)
        grid.set_margin_top(12)
        grid.set_margin_bottom(12)
        grid.set_margin_start(12)
        grid.set_margin_end(12)
        
        # Temperature unit setting
        unit_label = Gtk.Label(label="Temperature Unit:")
        unit_label.set_halign(Gtk.Align.START)
        
        unit_combo = Gtk.ComboBoxText()
        unit_combo.append("C", "Celsius (°C)")
        unit_combo.append("F", "Fahrenheit (°F)")
        unit_combo.set_active(0 if self.settings['temp_unit'] == 'C' else 1)
        
        # Update interval setting
        interval_label = Gtk.Label(label="Update Interval (seconds):")
        interval_label.set_halign(Gtk.Align.START)
        
        adjustment = Gtk.Adjustment(value=self.settings['update_interval'], 
                                  lower=1, upper=60, step_incr=1, page_incr=5)
        interval_spin = Gtk.SpinButton(adjustment=adjustment, climb_rate=1, digits=0)
        
        # Start at login setting
        login_switch = Gtk.Switch()
        login_switch.set_active(self.settings['start_at_login'])
        login_label = Gtk.Label(label="Start at login:")
        
        # Start minimized setting
        minimized_switch = Gtk.Switch()
        minimized_switch.set_active(self.settings['start_minimized'])
        minimized_label = Gtk.Label(label="Start minimized:")
        
        # Core selection
        core_label = Gtk.Label(label="Monitored Cores:")
        core_label.set_halign(Gtk.Align.START)
        
        core_box = Gtk.FlowBox()
        core_box.set_selection_mode(Gtk.SelectionMode.NONE)
        
        for i in range(psutil.cpu_count()):
            check = Gtk.CheckButton(label=f"Core {i}")
            check.set_active(i in self.settings['monitored_cores'])
            core_box.add(check)
        
        # Add widgets to grid
        grid.attach(unit_label, 0, 0, 1, 1)
        grid.attach(unit_combo, 1, 0, 1, 1)
        
        grid.attach(interval_label, 0, 1, 1, 1)
        grid.attach(interval_spin, 1, 1, 1, 1)
        
        grid.attach(login_label, 0, 2, 1, 1)
        grid.attach(login_switch, 1, 2, 1, 1)
        
        grid.attach(minimized_label, 0, 3, 1, 1)
        grid.attach(minimized_switch, 1, 3, 1, 1)
        
        grid.attach(core_label, 0, 4, 1, 1)
        grid.attach(core_box, 0, 5, 2, 1)
        
        content_area.pack_start(grid, True, True, 0)
        content_area.show_all()
        
        # Run the dialog
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            # Save settings
            self.settings['temp_unit'] = 'C' if unit_combo.get_active() == 0 else 'F'
            self.settings['update_interval'] = interval_spin.get_value_as_int()
            self.settings['start_at_login'] = login_switch.get_active()
            self.settings['start_minimized'] = minimized_switch.get_active()
            
            # Get selected cores
            self.settings['monitored_cores'] = []
            for i, child in enumerate(core_box.get_children()):
                if child.get_active():
                    self.settings['monitored_cores'].append(i)
            
            # Ensure at least one core is selected
            if not self.settings['monitored_cores']:
                self.settings['monitored_cores'] = [0]
            
            # Save settings to file
            self.save_settings()
            
            # Update data structures for new core selections
            self.initialize_data_structures()
            
            # Restart monitoring with new settings
            self.stop_monitoring()
            self.start_monitoring()
        
        dialog.destroy()
    
    def initialize_data_structures(self):
        # Re-initialize data storage with current settings
        self.timestamps = deque(maxlen=self.settings['max_data_points'])
        self.temps = {i: deque(maxlen=self.settings['max_data_points']) 
                     for i in self.settings['monitored_cores']}
        self.loads = {i: deque(maxlen=self.settings['max_data_points']) 
                     for i in self.settings['monitored_cores']}
    
    def on_window_delete(self, window, event):
        # Hide the window instead of closing the app
        window.hide()
        return True  # Prevent the default behavior (closing the window)
    
    def on_quit_clicked(self, widget):
        self.quit_application()
    
    def on_shutdown(self, app):
        self.stop_monitoring()
    
    def quit_application(self):
        self.stop_monitoring()
        self.app.quit()

def main():
    app = CoreMonApp()
    return app.app.run(None)

if __name__ == "__main__":
    main()
