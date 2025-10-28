#!/usr/bin/env python3

import subprocess
import time
import psutil

def test_coremon():
    """Test CoreMon functionality"""
    print("Testing CoreMon...")
    
    # Check if CoreMon is running
    coremon_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'coremon' in ' '.join(proc.info['cmdline'] or []):
                coremon_running = True
                print(f"✓ CoreMon is running (PID: {proc.info['pid']})")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not coremon_running:
        print("✗ CoreMon is not running")
        return False
    
    # Test CPU temperature reading
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            print("✓ CPU temperature sensors are available")
        else:
            print("! No temperature sensors found (using dummy data)")
    except AttributeError:
        print("! Temperature sensors not available (using dummy data)")
    
    # Test CPU load reading
    try:
        load = psutil.cpu_percent(interval=1)
        print(f"✓ CPU load reading: {load}%")
    except Exception as e:
        print(f"✗ Error reading CPU load: {e}")
        return False
    
    print("\nCoreMon test completed successfully!")
    return True

if __name__ == "__main__":
    test_coremon()
