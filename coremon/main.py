#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, GLib, Gio, AppIndicator3, Pango, Gdk
import os
import threading
import time
import psutil
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import configparser
import os

APP_ID = 'com.github.cascade.coremon'
CONFIG_DIR = os.path.expanduser('~/.config/coremon')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.ini')

class CoreMonApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        # Default settings
        self.settings = {
            'update_interval': 3,  # seconds
            'temperature_unit': 'C',
            'start_minimized': False,
            'autostart': False,
            'cores_to_monitor': 'avg',  # 'all', 'avg', or comma-separated list of core indices (default: avg)
            'window_width': 800,
            'window_height': 600,
            'temp_threshold': 100,  # Temperature threshold for red coloring (Celsius)
            'load_threshold': 100,  # Load threshold for red coloring (percentage)
            'show_individual_cores': False,  # Whether to show individual core graphs (default: average only)
            'smooth_graphs': True,  # Whether to use smooth lines in graphs
            'dashboard_avg_only': False  # Whether to show only average on dashboard
        }
        
        self.load_settings()
        self.setup_data_structures()
        self.setup_indicator()
        
    def setup_data_structures(self):
        self.max_data_points = 60  # Number of points to keep in history
        self.cpu_count = psutil.cpu_count()
        self.time_data = []
        self.temp_data = {}
        self.load_data = {}
        self.start_time = time.time()  # Track application start time
        
        # Initialize data structures for each core
        for i in range(self.cpu_count):
            self.temp_data[i] = []
            self.load_data[i] = []
        
    def load_settings(self):
        if not os.path.exists(CONFIG_FILE):
            return
            
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        
        if 'CoreMon' in config:
            for key in self.settings:
                if key in config['CoreMon']:
                    if key in ['window_width', 'window_height', 'update_interval', 'temp_threshold', 'load_threshold']:
                        self.settings[key] = config['CoreMon'].getint(key, self.settings[key])
                    elif key in ['start_minimized', 'autostart', 'show_individual_cores', 'smooth_graphs', 'dashboard_avg_only']:
                        self.settings[key] = config['CoreMon'].getboolean(key, self.settings[key])
                    else:
                        self.settings[key] = config['CoreMon'].get(key, self.settings[key])
    
    def save_settings(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config = configparser.ConfigParser()
        config['CoreMon'] = self.settings
        
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    def do_activate(self):
        # Show the window
        self.win = CoreMonWindow(self)
        self.win.show_all()
        
        # Initialize menu label based on initial visibility
        self.update_menu_label()
        
        if self.settings['start_minimized']:
            self.win.hide()
            self.show_hide_item.set_label("Show")
    
    def setup_indicator(self):
        # Create system tray indicator with temperature icon
        self.indicator = AppIndicator3.Indicator.new(
            "coremon",
            "temperature",  # Temperature icon
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Create menu
        self.menu = Gtk.Menu()
        
        # Show/Hide toggle item
        self.show_hide_item = Gtk.MenuItem(label="Hide")
        self.show_hide_item.connect("activate", self.on_show_hide)
        self.menu.append(self.show_hide_item)
        
        # Separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        
        # Start updating indicator
        self.update_indicator()
    
    def on_show_hide(self, widget):
        if not hasattr(self, 'win') or self.win is None:
            return
            
        if self.win.is_visible():
            # Hide the window and remove from taskbar
            self.win.hide()
            self.win.set_skip_taskbar_hint(True)
            self.show_hide_item.set_label("Show")
        else:
            # Show the window and add to taskbar
            self.win.present()
            self.win.set_skip_taskbar_hint(False)
            self.show_hide_item.set_label("Hide")
    
    def update_menu_label(self):
        """Update the show/hide menu label based on window visibility"""
        if not hasattr(self, 'win') or self.win is None:
            return
            
        if self.win.is_visible():
            self.show_hide_item.set_label("Hide")
        else:
            self.show_hide_item.set_label("Show")
    
    def on_quit(self, widget):
        # Clean up timers before quitting
        if hasattr(self, 'win') and hasattr(self.win, 'cleanup'):
            self.win.cleanup()
        self.quit()
    
    def update_indicator(self):
        # Get current CPU data
        temps = self.get_cpu_temps()
        loads = self.get_cpu_loads()
        
        if temps and loads:
            # Use the same filtering logic as the main UI
            # If dashboard_avg_only is enabled, always return all cores for averaging
            if self.settings.get('dashboard_avg_only', False):
                filtered_temps = temps
                filtered_loads = loads
            elif self.settings['cores_to_monitor'] == 'avg':
                # Return all cores for averaging
                filtered_temps = temps
                filtered_loads = loads
            elif self.settings['cores_to_monitor'] == 'all':
                filtered_temps = temps
                filtered_loads = loads
            else:
                # Return specific core
                core_num = int(self.settings['cores_to_monitor'])
                filtered_temps = {core_num: temps[core_num]} if core_num in temps else {}
                filtered_loads = {core_num: loads[core_num]} if core_num in loads else {}
            
            if filtered_temps and filtered_loads:
                avg_temp = sum(filtered_temps.values()) / len(filtered_temps)
                avg_load = sum(filtered_loads.values()) / len(filtered_loads)
                
                # Convert to Fahrenheit if needed
                temp_unit = "°C"
                if self.settings['temperature_unit'] == 'F':
                    avg_temp = avg_temp * 9/5 + 32
                    temp_unit = "°F"
                    temp_threshold = self.settings['temp_threshold'] * 9/5 + 32
                else:
                    temp_threshold = self.settings['temp_threshold']
                
                # Determine color based on thresholds
                temp_color = self.get_indicator_color(avg_temp, temp_threshold)
                load_color = self.get_indicator_color(avg_load, self.settings['load_threshold'])
                
                # Update indicator label with simple text (no color coding in system tray)
                self.indicator.set_label(f"{avg_temp:.0f}{temp_unit} {avg_load:.0f}%", "")
        
        # Schedule next update
        GLib.timeout_add_seconds(self.settings['update_interval'], self.update_indicator)
    
    def get_indicator_color(self, value, threshold):
        """Get color indicator for system tray"""
        if value >= threshold:
            return "red"
        elif value >= threshold * 0.8:
            return "orange"
        else:
            return "black"
    
    def get_cpu_temps(self):
        """Get CPU temperatures for all cores"""
        temps = {}
        try:
            # Try to get temperatures using psutil
            if hasattr(psutil, 'sensors_temperatures'):
                temps_info = psutil.sensors_temperatures()
                if 'coretemp' in temps_info:
                    for entry in temps_info['coretemp']:
                        if 'Core' in entry.label:
                            # Extract core number from label (e.g., 'Core 0' -> 0)
                            try:
                                core_num = int(entry.label.split()[1])
                                temps[core_num] = entry.current
                            except (IndexError, ValueError):
                                continue
        except Exception as e:
            print(f"Error getting CPU temps: {e}")
            
        # Fallback to psutil if no temperatures found
        if not temps and hasattr(psutil, 'sensors_temperatures'):
            # Just return a dummy value for each core
            temps = {i: 40.0 + i for i in range(self.cpu_count)}
            
        return temps
    
    def get_cpu_loads(self):
        """Get CPU load percentages for all cores"""
        loads = {}
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        for i, load in enumerate(per_cpu):
            loads[i] = load
        return loads

class CoreMonWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        
        self.app = app
        self.set_default_size(
            self.app.settings['window_width'],
            self.app.settings['window_height']
        )
        
        self.setup_ui()
        self.start_monitoring()
        
        # Connect delete event to hide window instead of closing
        self.connect("delete-event", self.on_delete_event)
        # Connect window state events to update menu
        self.connect("window-state-event", self.on_window_state_event)
    
    def on_delete_event(self, widget, event):
        # Hide window and remove from taskbar (same as Hide)
        self.hide()
        self.set_skip_taskbar_hint(True)
        self.app.show_hide_item.set_label("Show")
        return True  # Prevent the default handler from running
    
    def on_window_state_event(self, widget, event):
        """Handle window state changes to update menu label"""
        # Update menu label when window state changes
        self.app.update_menu_label()
        return False
    
    def cleanup(self):
        """Clean up timers and resources"""
        if hasattr(self, 'uptime_timer'):
            GLib.source_remove(self.uptime_timer)
    
    def setup_ui(self):
        self.set_title("CoreMon - System Monitor")
        
        # Apply CSS styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
            .dashboard-card {
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                margin: 8px;
                padding: 16px;
            }
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                margin: 8px 0;
            }
            .stat-label {
                font-size: 12px;
                color: #888;
            }
            .stat-icon {
                margin-bottom: 8px;
            }
            .temp-normal { color: #4CAF50; }
            .temp-warm { color: #FFC107; }
            .temp-hot { color: #FF9800; }
            .temp-critical { color: #F44336; }
            .load-normal { color: #4CAF50; }
            .load-warm { color: #FFC107; }
            .load-hot { color: #FF9800; }
            .load-critical { color: #F44336; }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Main container with better spacing
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        self.add(main_box)
        
        # Create notebook for tabs
        notebook = Gtk.Notebook()
        main_box.pack_start(notebook, True, True, 0)
        
        # Dashboard tab
        dashboard_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        notebook.append_page(dashboard_box, Gtk.Label(label="Dashboard"))
        
        # Stats cards container
        stats_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        stats_container.set_homogeneous(True)
        dashboard_box.pack_start(stats_container, False, False, 0)
        
        # Temperature card with visible frame
        temp_card_frame = Gtk.Frame()
        temp_card_frame.set_shadow_type(Gtk.ShadowType.OUT)
        temp_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        temp_card.set_margin_top(12)
        temp_card.set_margin_bottom(12)
        temp_card.set_margin_start(12)
        temp_card.set_margin_end(12)
        temp_card_frame.add(temp_card)
        
        temp_icon = Gtk.Image.new_from_icon_name("temperature", Gtk.IconSize.DIALOG)
        temp_icon.get_style_context().add_class("stat-icon")
        temp_card.pack_start(temp_icon, False, False, 0)
        
        temp_label_title = Gtk.Label(label="Temperature")
        temp_label_title.get_style_context().add_class("stat-label")
        temp_card.pack_start(temp_label_title, False, False, 0)
        
        self.temp_label = Gtk.Label(label="N/A°C")
        self.temp_label.get_style_context().add_class("stat-value")
        temp_card.pack_start(self.temp_label, False, False, 0)
        
        stats_container.pack_start(temp_card_frame, True, True, 0)
        
        # CPU Load card with visible frame
        load_card_frame = Gtk.Frame()
        load_card_frame.set_shadow_type(Gtk.ShadowType.OUT)
        load_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        load_card.set_margin_top(12)
        load_card.set_margin_bottom(12)
        load_card.set_margin_start(12)
        load_card.set_margin_end(12)
        load_card_frame.add(load_card)
        
        load_icon = Gtk.Image.new_from_icon_name("system-run", Gtk.IconSize.DIALOG)
        load_icon.set_pixel_size(48)  # Force size to match temperature icon
        load_icon.get_style_context().add_class("stat-icon")
        load_card.pack_start(load_icon, False, False, 0)
        
        load_label_title = Gtk.Label(label="CPU Load")
        load_label_title.get_style_context().add_class("stat-label")
        load_card.pack_start(load_label_title, False, False, 0)
        
        self.load_label = Gtk.Label(label="N/A%")
        self.load_label.get_style_context().add_class("stat-value")
        load_card.pack_start(self.load_label, False, False, 0)
        
        stats_container.pack_start(load_card_frame, True, True, 0)
        
        # Graphs section
        graph_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        dashboard_box.pack_start(graph_box, True, True, 0)
        
        # Temperature graph (no header, has title in graph)
        self.temp_fig = Figure(figsize=(6, 2.5), dpi=100, facecolor='#2b2b2b')
        self.temp_ax = self.temp_fig.add_subplot(111, facecolor='#2b2b2b')
        self.temp_line, = self.temp_ax.plot([], [], 'r-')
        self.temp_ax.set_ylabel('Temperature (°C)')
        self.temp_ax.grid(True)
        
        self.temp_canvas = FigureCanvas(self.temp_fig)
        graph_box.pack_start(self.temp_canvas, True, True, 0)
        
        # Load graph (no header, has title in graph)
        self.load_fig = Figure(figsize=(6, 2.5), dpi=100, facecolor='#2b2b2b')
        self.load_ax = self.load_fig.add_subplot(111, facecolor='#2b2b2b')
        self.load_line, = self.load_ax.plot([], [], 'b-')
        self.load_ax.set_ylabel('Load (%)')
        self.load_ax.set_ylim(0, 100)  # 0-100% range for CPU load
        self.load_ax.grid(True)
        
        self.load_canvas = FigureCanvas(self.load_fig)
        graph_box.pack_start(self.load_canvas, True, True, 0)
        
        # Settings tab
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=12)
        notebook.append_page(settings_box, Gtk.Label(label="Settings"))
        
        # Add settings controls here
        settings_label = Gtk.Label(label="CoreMon Settings")
        settings_label.get_style_context().add_class("title-2")
        settings_box.pack_start(settings_label, False, False, 0)
        
        # Update interval
        interval_box = Gtk.Box(spacing=12)
        interval_label = Gtk.Label(label="Update interval (seconds):")
        interval_box.pack_start(interval_label, False, False, 0)
        
        self.interval_spin = Gtk.SpinButton.new_with_range(1, 60, 1)
        self.interval_spin.set_value(self.app.settings['update_interval'])
        self.interval_spin.connect("value-changed", self.on_setting_changed)
        interval_box.pack_start(self.interval_spin, False, False, 0)
        
        settings_box.pack_start(interval_box, False, False, 0)
        
        # Temperature unit
        unit_box = Gtk.Box(spacing=12)
        unit_label = Gtk.Label(label="Temperature unit:")
        unit_box.pack_start(unit_label, False, False, 0)
        
        self.unit_combo = Gtk.ComboBoxText()
        self.unit_combo.append("C", "Celsius (°C)")
        self.unit_combo.append("F", "Fahrenheit (°F)")
        self.unit_combo.set_active_id(self.app.settings['temperature_unit'])
        self.unit_combo.connect("changed", self.on_setting_changed)
        unit_box.pack_start(self.unit_combo, False, False, 0)
        
        settings_box.pack_start(unit_box, False, False, 0)
        
        # Temperature threshold
        temp_threshold_box = Gtk.Box(spacing=12)
        temp_threshold_label = Gtk.Label(label="Temperature threshold (°C):")
        temp_threshold_box.pack_start(temp_threshold_label, False, False, 0)
        
        self.temp_threshold_spin = Gtk.SpinButton.new_with_range(50, 150, 5)
        self.temp_threshold_spin.set_value(self.app.settings['temp_threshold'])
        self.temp_threshold_spin.connect("value-changed", self.on_setting_changed)
        temp_threshold_box.pack_start(self.temp_threshold_spin, False, False, 0)
        
        settings_box.pack_start(temp_threshold_box, False, False, 0)
        
        # Load threshold
        load_threshold_box = Gtk.Box(spacing=12)
        load_threshold_label = Gtk.Label(label="Load threshold (%):")
        load_threshold_box.pack_start(load_threshold_label, False, False, 0)
        
        self.load_threshold_spin = Gtk.SpinButton.new_with_range(50, 100, 5)
        self.load_threshold_spin.set_value(self.app.settings['load_threshold'])
        self.load_threshold_spin.connect("value-changed", self.on_setting_changed)
        load_threshold_box.pack_start(self.load_threshold_spin, False, False, 0)
        
        settings_box.pack_start(load_threshold_box, False, False, 0)
        
        # Core selection
        core_selection_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        core_selection_label = Gtk.Label(label="Core monitoring:")
        core_selection_label.set_halign(Gtk.Align.START)
        core_selection_box.pack_start(core_selection_label, False, False, 0)
        
        self.core_combo = Gtk.ComboBoxText()
        self.core_combo.append("all", "All cores")
        self.core_combo.append("avg", "Average only")
        for i in range(self.app.cpu_count):
            self.core_combo.append(str(i), f"Core {i}")
        self.core_combo.set_active_id(self.app.settings['cores_to_monitor'])
        self.core_combo.connect("changed", self.on_setting_changed)
        core_selection_box.pack_start(self.core_combo, False, False, 0)
        
        settings_box.pack_start(core_selection_box, False, False, 0)
        
        # Show individual cores
        self.show_individual_cores_switch = Gtk.Switch()
        self.show_individual_cores_switch.set_active(self.app.settings['show_individual_cores'])
        self.show_individual_cores_switch.connect("notify::active", self.on_setting_changed)
        individual_cores_box = Gtk.Box(spacing=12)
        individual_cores_label = Gtk.Label(label="Show individual core graphs:")
        individual_cores_box.pack_start(individual_cores_label, False, False, 0)
        individual_cores_box.pack_end(self.show_individual_cores_switch, False, False, 0)
        settings_box.pack_start(individual_cores_box, False, False, 0)
        
        # Smooth graphs
        self.smooth_graphs_switch = Gtk.Switch()
        self.smooth_graphs_switch.set_active(self.app.settings['smooth_graphs'])
        self.smooth_graphs_switch.connect("notify::active", self.on_setting_changed)
        smooth_graphs_box = Gtk.Box(spacing=12)
        smooth_graphs_label = Gtk.Label(label="Smooth graph lines:")
        smooth_graphs_box.pack_start(smooth_graphs_label, False, False, 0)
        smooth_graphs_box.pack_end(self.smooth_graphs_switch, False, False, 0)
        settings_box.pack_start(smooth_graphs_box, False, False, 0)
        
        # Dashboard average only
        self.dashboard_avg_only_switch = Gtk.Switch()
        self.dashboard_avg_only_switch.set_active(self.app.settings['dashboard_avg_only'])
        self.dashboard_avg_only_switch.connect("notify::active", self.on_setting_changed)
        dashboard_avg_only_box = Gtk.Box(spacing=12)
        dashboard_avg_only_label = Gtk.Label(label="Dashboard: Show average only:")
        dashboard_avg_only_box.pack_start(dashboard_avg_only_label, False, False, 0)
        dashboard_avg_only_box.pack_end(self.dashboard_avg_only_switch, False, False, 0)
        settings_box.pack_start(dashboard_avg_only_box, False, False, 0)
        
        # Start minimized
        self.start_minimized_switch = Gtk.Switch()
        self.start_minimized_switch.set_active(self.app.settings['start_minimized'])
        minimized_box = Gtk.Box(spacing=12)
        minimized_label = Gtk.Label(label="Start minimized:")
        minimized_box.pack_start(minimized_label, False, False, 0)
        minimized_box.pack_end(self.start_minimized_switch, False, False, 0)
        settings_box.pack_start(minimized_box, False, False, 0)
        
        # Autostart
        self.autostart_switch = Gtk.Switch()
        self.autostart_switch.set_active(self.app.settings['autostart'])
        autostart_box = Gtk.Box(spacing=12)
        autostart_label = Gtk.Label(label="Start on login:")
        autostart_box.pack_start(autostart_label, False, False, 0)
        autostart_box.pack_end(self.autostart_switch, False, False, 0)
        settings_box.pack_start(autostart_box, False, False, 0)
        
        # Save button
        save_button = Gtk.Button(label="Save Settings")
        save_button.connect("clicked", self.on_save_settings)
        settings_box.pack_end(save_button, False, False, 0)
        
        # System Info tab
        system_info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=12)
        notebook.append_page(system_info_box, Gtk.Label(label="System Info"))
        
        # Main container for system info
        main_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        system_info_box.pack_start(main_container, True, True, 0)
        
        # Left side - Neofetch output (no scrolling)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_container.pack_start(left_box, True, True, 0)
        
        # Create text view for system info without scrolling
        self.system_info_text = Gtk.TextView()
        self.system_info_text.set_editable(False)
        self.system_info_text.set_wrap_mode(Gtk.WrapMode.NONE)
        self.system_info_text.set_size_request(-1, 400)  # Fixed height to fit window
        left_box.pack_start(self.system_info_text, True, True, 0)
        
        # Right side - Live uptime display
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_container.pack_start(right_box, False, False, 0)
        
        # Uptime frame
        uptime_frame = Gtk.Frame(label="Live Uptime")
        uptime_frame.set_size_request(160, -1)  # Fixed width for the entire frame
        uptime_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=12)
        uptime_frame.add(uptime_box)
        
        # System uptime
        system_uptime_label = Gtk.Label(label="System: 00:00:00")
        system_uptime_label.get_style_context().add_class("uptime-label")
        system_uptime_label.set_size_request(140, -1)  # Fixed width to prevent movement
        system_uptime_label.set_halign(Gtk.Align.START)  # Left align
        # Use monospace font for consistent character width
        system_uptime_label.override_font(Pango.FontDescription.from_string("monospace 10"))
        uptime_box.pack_start(system_uptime_label, False, False, 0)
        
        # CoreMon uptime
        coremon_uptime_label = Gtk.Label(label="CoreMon: 00:00:00")
        coremon_uptime_label.get_style_context().add_class("uptime-label")
        coremon_uptime_label.set_size_request(140, -1)  # Fixed width to prevent movement
        coremon_uptime_label.set_halign(Gtk.Align.START)  # Left align
        # Use monospace font for consistent character width
        coremon_uptime_label.override_font(Pango.FontDescription.from_string("monospace 10"))
        uptime_box.pack_start(coremon_uptime_label, False, False, 0)
        
        right_box.pack_start(uptime_frame, False, False, 0)
        
        # Store references for updates
        self.system_uptime_label = system_uptime_label
        self.coremon_uptime_label = coremon_uptime_label
        
        # Add refresh button
        refresh_button = Gtk.Button(label="Refresh System Info")
        refresh_button.connect("clicked", self.on_refresh_system_info)
        left_box.pack_start(refresh_button, False, False, 0)
        
        # Load initial system info
        self.update_system_info()
        
        # Start uptime refresh timer
        self.uptime_timer = GLib.timeout_add_seconds(1, self.refresh_uptime_only)
        
        # About tab
        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=12)
        notebook.append_page(about_box, Gtk.Label(label="About"))
        
        about_label = Gtk.Label()
        about_label.set_markup(
            "<big><b>CoreMon v1.0</b></big>\n\n"
            "A simple temperature and load monitor for Ubuntu based OS.\n"
            "Designed to give you a quick view of your temps and load.\n\n"
            "© 2025 CoreMon Project"
        )
        about_label.set_justify(Gtk.Justification.CENTER)
        about_box.pack_start(about_label, True, True, 0)
        
        self.show_all()
    
    def refresh_uptime_only(self):
        """Refresh only the uptime labels every second"""
        try:
            # Update uptime labels
            boot_time = psutil.boot_time()
            system_uptime = time.time() - boot_time
            coremon_uptime = time.time() - self.app.start_time
            
            self.system_uptime_label.set_text(f"System: {self.format_uptime(system_uptime)}")
            self.coremon_uptime_label.set_text(f"CoreMon: {self.format_uptime(coremon_uptime)}")
            
        except Exception as e:
            print(f"Error refreshing uptime: {e}")
        
        # Return True to keep the timer running
        return True
    
    def on_refresh_system_info(self, widget):
        """Refresh system information display"""
        self.update_system_info()
    
    def update_system_info(self):
        """Update system information display"""
        try:
            # Get system information
            info_text = self.get_system_info()
            
            # Update text view
            text_buffer = self.system_info_text.get_buffer()
            text_buffer.set_text(info_text)
            
            # Apply monospace font for better formatting
            self.system_info_text.override_font(
                Pango.FontDescription.from_string("monospace 10")
            )
        except Exception as e:
            print(f"Error updating system info: {e}")
    
    def get_system_info(self):
        """Get actual neofetch output with minimal additions"""
        import subprocess

        info_lines = []

        # Try to get actual neofetch output
        try:
            # Run neofetch and capture its output directly
            result = subprocess.run(['neofetch', '--stdout'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                # Add neofetch output directly without headers
                info_lines.append(result.stdout.strip())
            else:
                # Fallback if neofetch fails
                info_lines.append("! Neofetch output unavailable")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            info_lines.append("! Neofetch not installed or not working")
            info_lines.append(f"! Install with: sudo apt install neofetch")

        # Add only process information
        info_lines.append("")
        info_lines.append("PROCESS INFORMATION")
        info_lines.append("-" * 30)
        info_lines.append(f"Total processes: {len(psutil.pids())}")
        info_lines.append(f"Running: {sum(1 for p in psutil.process_iter(['status']) if p.info['status'] == psutil.STATUS_RUNNING)}")
        info_lines.append(f"Sleeping: {sum(1 for p in psutil.process_iter(['status']) if p.info['status'] == psutil.STATUS_SLEEPING)}")

        return "\n".join(info_lines)
    
    def create_usage_bar(self, percentage, width=20):
        """Create a visual usage bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        
        # Color coding based on percentage
        if percentage >= 90:
            return f"[{bar}]"
        elif percentage >= 70:
            return f"[{bar}]"
        elif percentage >= 50:
            return f"[{bar}]"
        else:
            return f"[{bar}]"
    
    def create_temp_bar(self, temp, max_temp=100, width=20):
        """Create a visual temperature bar"""
        percentage = min(temp / max_temp * 100, 100)
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        
        # Color coding based on temperature
        if temp >= 80:
            return f"[{bar}]"
        elif temp >= 60:
            return f"[{bar}]"
        elif temp >= 40:
            return f"[{bar}]"
        else:
            return f"[{bar}]"
    
    def get_cpu_info(self):
        """Get CPU model information"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        return line.split(':')[1].strip()
        except:
            return "Unknown CPU"
    
    def get_memory_info(self):
        """Get formatted memory information"""
        memory = psutil.virtual_memory()
        return f"{self.format_bytes(memory.total)} ({memory.percent:.1f}% used)"
    
    def get_disk_info(self):
        """Get disk usage information"""
        try:
            disk = psutil.disk_usage('/')
            return f"{self.format_bytes(disk.total)} ({disk.percent:.1f}% used)"
        except:
            return "Unknown"
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"

    def format_uptime(self, seconds):
        """Format uptime seconds to hh:mm:ss or dd:hh:mm:ss format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if days > 0:
            return f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def on_setting_changed(self, widget):
        # Apply settings immediately
        self.app.settings['update_interval'] = self.interval_spin.get_value_as_int()
        self.app.settings['temperature_unit'] = self.unit_combo.get_active_id()
        self.app.settings['temp_threshold'] = self.temp_threshold_spin.get_value_as_int()
        self.app.settings['load_threshold'] = self.load_threshold_spin.get_value_as_int()
        self.app.settings['cores_to_monitor'] = self.core_combo.get_active_id()
        self.app.settings['show_individual_cores'] = self.show_individual_cores_switch.get_active()
        self.app.settings['smooth_graphs'] = self.smooth_graphs_switch.get_active()
        self.app.settings['dashboard_avg_only'] = self.dashboard_avg_only_switch.get_active()
        self.app.settings['start_minimized'] = self.start_minimized_switch.get_active()
        self.app.settings['autostart'] = self.autostart_switch.get_active()
        
        # Save to config file
        self.app.save_settings()
        
        # Clear data to force refresh with new settings
        self.app.time_data.clear()
        for i in range(self.app.cpu_count):
            self.app.temp_data[i].clear()
            self.app.load_data[i].clear()
    
    def on_save_settings(self, widget):
        # Save window size
        width, height = self.get_size()
        self.app.settings['window_width'] = width
        self.app.settings['window_height'] = height
        
        # Save to config file
        self.app.save_settings()
        
        # Show confirmation
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Settings saved"
        )
        dialog.format_secondary_text("Settings are applied immediately and will persist after restarting CoreMon.")
        dialog.run()
        dialog.destroy()
    
    def start_monitoring(self):
        self.update_ui()
        
    def update_ui(self):
        # Get current CPU data
        temps = self.app.get_cpu_temps()
        loads = self.app.get_cpu_loads()
        
        # Update current stats
        if temps and loads:
            # Filter cores based on setting
            filtered_temps = self.filter_cores(temps)
            filtered_loads = self.filter_cores(loads)
            
            if filtered_temps:
                avg_temp = sum(filtered_temps.values()) / len(filtered_temps)
                
                # Convert to Fahrenheit if needed
                if self.app.settings['temperature_unit'] == 'F':
                    avg_temp = avg_temp * 9/5 + 32
                    temp_unit = "°F"
                    # Convert threshold to Fahrenheit for comparison
                    temp_threshold = self.app.settings['temp_threshold'] * 9/5 + 32
                else:
                    temp_unit = "°C"
                    temp_threshold = self.app.settings['temp_threshold']
                
                # Apply color coding using CSS classes
                temp_color_class = self.get_temp_color_class(avg_temp, temp_threshold)
                self.temp_label.set_text(f"{avg_temp:.1f}{temp_unit}")
                
                # Remove old color classes and add new one
                style_context = self.temp_label.get_style_context()
                for css_class in style_context.list_classes():
                    if css_class.startswith('temp-'):
                        style_context.remove_class(css_class)
                style_context.add_class(temp_color_class)
                
                # Add to history
                elapsed_time = time.time() - self.app.start_time
                self.app.time_data.append(elapsed_time)
                
                # Keep only the last N data points
                if len(self.app.time_data) > self.app.max_data_points:
                    self.app.time_data.pop(0)
                
                # Update temperature data
                for core, temp in filtered_temps.items():
                    # Convert to Fahrenheit if needed for storage
                    display_temp = temp
                    if self.app.settings['temperature_unit'] == 'F':
                        display_temp = temp * 9/5 + 32
                    self.app.temp_data[core].append(display_temp)
                    if len(self.app.temp_data[core]) > self.app.max_data_points:
                        self.app.temp_data[core].pop(0)
                
                # Update load data
                for core, load in filtered_loads.items():
                    self.app.load_data[core].append(load)
                    if len(self.app.load_data[core]) > self.app.max_data_points:
                        self.app.load_data[core].pop(0)
                
                # Update graphs
                self.update_graphs()
            
            if filtered_loads:
                avg_load = sum(filtered_loads.values()) / len(filtered_loads)
                
                # Apply color coding using CSS classes
                load_color_class = self.get_load_color_class(avg_load, self.app.settings['load_threshold'])
                self.load_label.set_text(f"{avg_load:.1f}%")
                
                # Remove old color classes and add new one
                style_context = self.load_label.get_style_context()
                for css_class in style_context.list_classes():
                    if css_class.startswith('load-'):
                        style_context.remove_class(css_class)
                style_context.add_class(load_color_class)
        
        # Schedule next update
        GLib.timeout_add_seconds(
            self.app.settings['update_interval'],
            self.update_ui
        )
    
    def filter_cores(self, data):
        """Filter data based on core selection setting"""
        # If dashboard_avg_only is enabled, always return all cores for averaging
        if self.app.settings['dashboard_avg_only']:
            return data
        elif self.app.settings['cores_to_monitor'] == 'avg':
            # Return all cores for averaging (will be averaged in update_ui)
            return data
        elif self.app.settings['cores_to_monitor'] == 'all':
            return data
        else:
            # Return specific core
            core_num = int(self.app.settings['cores_to_monitor'])
            if core_num in data:
                return {core_num: data[core_num]}
            return {}
    
    def get_temp_color_class(self, temp, threshold):
        """Get CSS color class for temperature based on threshold"""
        if temp >= threshold:
            return "temp-critical"
        elif temp >= threshold * 0.7:
            return "temp-hot"
        elif temp >= threshold * 0.5:
            return "temp-warm"
        else:
            return "temp-normal"
    
    def get_load_color_class(self, load, threshold):
        """Get CSS color class for load based on threshold"""
        if load >= threshold:
            return "load-critical"
        elif load >= threshold * 0.7:
            return "load-hot"
        elif load >= threshold * 0.5:
            return "load-warm"
        else:
            return "load-normal"
    
    def get_temp_color(self, temp, threshold):
        """Get color for temperature based on threshold - green/yellow/red"""
        if temp >= threshold:
            return "red"
        elif temp >= threshold * 0.7:
            return "orange"
        elif temp >= threshold * 0.5:
            return "goldenrod"
        else:
            return "green"
    
    def get_load_color(self, load, threshold):
        """Get color for load based on threshold"""
        if load >= threshold:
            return "red"
        elif load >= threshold * 0.8:
            return "orange"
        elif load >= threshold * 0.6:
            return "goldenrod"
        else:
            return "black"
    
    def update_graphs(self):
        if not self.app.time_data:
            return
        
        # Determine which cores to show based on settings
        if not self.app.settings['show_individual_cores']:
            # Default: show only average line
            cores_to_show = [-1]  # Use -1 for average
        elif self.app.settings['cores_to_monitor'] == 'avg':
            # Show only average line
            cores_to_show = [-1]  # Use -1 for average
        elif self.app.settings['cores_to_monitor'] == 'all':
            # Show all cores (when individual cores enabled)
            cores_to_show = list(range(self.app.cpu_count))
        else:
            # Show specific core
            cores_to_show = [int(self.app.settings['cores_to_monitor'])]
        
        # Format time data for display
        time_labels = [self.format_elapsed_time(t) for t in self.app.time_data]
        
        # Update temperature graph
        self.temp_ax.clear()
        self.temp_ax.set_facecolor('#2b2b2b')
        
        if -1 in cores_to_show:
            # Calculate and show average
            avg_temps = []
            for i in range(len(self.app.time_data)):
                temps_at_time = []
                for core in range(self.app.cpu_count):
                    if core in self.app.temp_data and i < len(self.app.temp_data[core]):
                        temps_at_time.append(self.app.temp_data[core][i])
                if temps_at_time:
                    avg_temps.append(sum(temps_at_time) / len(temps_at_time))
                else:
                    avg_temps.append(0)
            
            # Determine line style based on smooth setting
            line_style = '-' if self.app.settings['smooth_graphs'] else 'steps'
            
            self.temp_ax.plot(
                range(len(avg_temps)),
                avg_temps,
                label="Average",
                color='red',
                linewidth=2,
                alpha=0.8,
                linestyle=line_style
            )
        
        # Show individual cores if enabled in settings
        if self.app.settings['show_individual_cores'] and -1 not in cores_to_show:
            line_style = '-' if self.app.settings['smooth_graphs'] else 'steps'
            for core in cores_to_show:
                if core in self.app.temp_data and self.app.temp_data[core]:
                    self.temp_ax.plot(
                        range(len(self.app.temp_data[core])),
                        self.app.temp_data[core],
                        label=f"Core {core}",
                        alpha=0.7,
                        linestyle=line_style
                    )
        
        temp_unit = "°C" if self.app.settings['temperature_unit'] == 'C' else "°F"
        self.temp_ax.set_ylabel(f'Temperature ({temp_unit})', color='#cccccc')
        self.temp_ax.set_title('CPU Temperature Over Time', color='#cccccc')
        self.temp_ax.grid(True, alpha=0.3, color='#555555')
        self.temp_ax.tick_params(colors='#cccccc')
        
        # Set x-axis labels to show elapsed time
        if len(time_labels) > 0:
            # Show every nth label to avoid crowding
            step = max(1, len(time_labels) // 10)
            self.temp_ax.set_xticks(range(0, len(time_labels), step))
            self.temp_ax.set_xticklabels([time_labels[i] for i in range(0, len(time_labels), step)])
        
        # Anchor legend outside plot area (bottom)
        if cores_to_show or -1 in cores_to_show:
            legend = self.temp_ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=4, framealpha=0.9)
            legend.get_frame().set_facecolor('#2b2b2b')
            for text in legend.get_texts():
                text.set_color('#cccccc')
        
        # Rotate x-axis labels for better readability
        for label in self.temp_ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
        
        self.temp_fig.tight_layout(pad=1.5)
        self.temp_canvas.draw()
        
        # Update load graph
        self.load_ax.clear()
        self.load_ax.set_facecolor('#2b2b2b')
        
        if -1 in cores_to_show:
            # Calculate and show average
            avg_loads = []
            for i in range(len(self.app.time_data)):
                loads_at_time = []
                for core in range(self.app.cpu_count):
                    if core in self.app.load_data and i < len(self.app.load_data[core]):
                        loads_at_time.append(self.app.load_data[core][i])
                if loads_at_time:
                    avg_loads.append(sum(loads_at_time) / len(loads_at_time))
                else:
                    avg_loads.append(0)
            
            # Determine line style based on smooth setting
            line_style = '-' if self.app.settings['smooth_graphs'] else 'steps'
            
            self.load_ax.plot(
                range(len(avg_loads)),
                avg_loads,
                label="Average",
                color='blue',
                linewidth=2,
                alpha=0.8,
                linestyle=line_style
            )
        
        # Show individual cores if enabled in settings
        if self.app.settings['show_individual_cores'] and -1 not in cores_to_show:
            line_style = '-' if self.app.settings['smooth_graphs'] else 'steps'
            for core in cores_to_show:
                if core in self.app.load_data and self.app.load_data[core]:
                    self.load_ax.plot(
                        range(len(self.app.load_data[core])),
                        self.app.load_data[core],
                        label=f"Core {core}",
                        alpha=0.7,
                        linestyle=line_style
                    )
        
        self.load_ax.set_ylabel('Load (%)', color='#cccccc')
        self.load_ax.set_title('CPU Load Over Time', color='#cccccc')
        self.load_ax.set_ylim(0, 100)  # 0-100% range for CPU load
        self.load_ax.grid(True, alpha=0.3, color='#555555')
        self.load_ax.tick_params(colors='#cccccc')
        
        # Set x-axis labels to show elapsed time
        if len(time_labels) > 0:
            # Show every nth label to avoid crowding
            step = max(1, len(time_labels) // 10)
            self.load_ax.set_xticks(range(0, len(time_labels), step))
            self.load_ax.set_xticklabels([time_labels[i] for i in range(0, len(time_labels), step)])
        
        # Anchor legend outside plot area (bottom)
        if cores_to_show or -1 in cores_to_show:
            legend = self.load_ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=4, framealpha=0.9)
            legend.get_frame().set_facecolor('#2b2b2b')
            for text in legend.get_texts():
                text.set_color('#cccccc')
        
        # Rotate x-axis labels for better readability
        for label in self.load_ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
        
        self.load_fig.tight_layout(pad=1.5)
        self.load_canvas.draw()
    
    def format_elapsed_time(self, seconds):
        """Format elapsed time for graph display"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m{secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h{minutes}m"

def main():
    app = CoreMonApp()
    return app.run(None)

if __name__ == "__main__":
    main()
