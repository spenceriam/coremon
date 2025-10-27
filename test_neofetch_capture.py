#!/usr/bin/env python3

import subprocess

def test_neofetch_capture():
    """Test that we're capturing neofetch output exactly as it appears"""
    print("🔍 TESTING NEOFETCH OUTPUT CAPTURE")
    print("=" * 50)
    
    # Test neofetch command exactly as CoreMon does it
    try:
        result = subprocess.run(['neofetch', '--stdout'],
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Successfully captured neofetch output!")
            print("\n📋 RAW NEOFETCH OUTPUT (as CoreMon sees it):")
            print("-" * 50)
            print(repr(result.stdout[:200]))  # Show first 200 chars as repr
            print("...")
            print("-" * 50)
            print("\n🖥️ FORMATTED NEOFETCH OUTPUT:")
            print(result.stdout)
            print("-" * 50)
            
            # Check for ASCII art
            lines = result.stdout.split('\n')
            print(f"\n📊 OUTPUT ANALYSIS:")
            print(f"  Total lines: {len(lines)}")
            print(f"  Has ASCII art: {any('     ' in line or '___' in line or '/   \\' in line for line in lines[:10])}")
            print(f"  Has system info: {any('OS:' in line or 'CPU:' in line or 'Memory:' in line for line in lines)}")
            
            # Show first few lines to verify ASCII art
            print(f"\n🎨 FIRST 10 LINES (should show ASCII art):")
            for i, line in enumerate(lines[:10]):
                print(f"  {i+1:2d}: {repr(line)}")
                
        else:
            print("❌ Neofetch command failed or returned empty output")
            print(f"Return code: {result.returncode}")
            print(f"Stdout: {repr(result.stdout)}")
            print(f"Stderr: {repr(result.stderr)}")
            
    except Exception as e:
        print(f"❌ Error running neofetch: {e}")
    
    print("\n✅ EXPECTED BEHAVIOR:")
    print("  • CoreMon should show EXACT neofetch output")
    print("  • ASCII art should be preserved")
    print("  • All system info should be intact")
    print("  • No modifications to neofetch output")
    print("  • CoreMon sensor data added below")

if __name__ == "__main__":
    test_neofetch_capture()
