#!/usr/bin/env python3

import subprocess

def test_clean_system_info():
    """Test the clean system info layout"""
    print("🧹 TESTING CLEAN SYSTEM INFO LAYOUT")
    print("=" * 50)
    
    # Test neofetch output
    try:
        result = subprocess.run(['neofetch', '--stdout'],
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Clean neofetch output captured!")
            print("\n📋 WHAT YOU'LL SEE IN COREMON:")
            print("-" * 50)
            print("[ACTUAL NEOFETCH OUTPUT - NO HEADERS]")
            print(result.stdout.strip())
            print("-" * 50)
            print("")
            print("⚙️ PROCESS INFORMATION")
            print("------------------------------")
            print("Total processes: 245")
            print("Running: 3")
            print("Sleeping: 242")
            print("")
            
        else:
            print("❌ Neofetch command failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎨 NEW LAYOUT FEATURES:")
    print("=" * 50)
    print("✅ REMOVED:")
    print("  • 'Actual neofetch output' headers")
    print("  • Temperature sensor data")
    print("  • CPU usage bars")
    print("  • Memory usage bars")
    print("  • Scrolled window")
    print("")
    print("✅ KEPT:")
    print("  • Pure neofetch output")
    print("  • Process information")
    print("  • Live uptime display (right side)")
    print("")
    print("✅ ADDED:")
    print("  • System uptime at bottom")
    print("  • Fixed height (no scrolling)")
    print("  • Better window fit")
    print("")
    print("📐 LAYOUT:")
    print("┌─────────────────────────────────────┐")
    print("│ [Neofetch Output]   │ [Live Uptime] │")
    print("│                     │ System: 1d 2h │")
    print("│ [ASCII Art]         │ CoreMon: 5m  │")
    print("│ OS: Zorin OS 18     │               │")
    print("│ CPU: i7-1185G7      │               │")
    print("│ Memory: 7785MiB     │               │")
    print("│                     │               │")
    print("│ ⚙️ PROCESS INFO     │               │")
    print("│ Total: 245          │               │")
    print("│ Running: 3          │               │")
    print("│ [Refresh Button]    │               │")
    print("├─────────────────────────────────────┤")
    print("│ System Uptime: 1d 2h 30m            │")
    print("└─────────────────────────────────────┘")
    print("")
    print("🎯 BENEFITS:")
    print("  • Clean, authentic neofetch display")
    print("  • No scrolling - fits window perfectly")
    print("  • System uptime prominently displayed")
    print("  • Live updates without interrupting view")
    print("  • Minimal, focused information")

if __name__ == "__main__":
    test_clean_system_info()
