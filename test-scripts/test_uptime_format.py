#!/usr/bin/env python3

def format_uptime(seconds):
    """Format uptime seconds to hh:mm:ss or dd:hh:mm:ss format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if days > 0:
        return f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def test_uptime_format():
    """Test the new uptime format"""
    print("⏰ TESTING NEW UPTIME FORMAT")
    print("=" * 50)
    
    test_cases = [
        (45, "Less than 1 minute"),
        (125, "About 2 minutes"),
        (3661, "About 1 hour"),
        (7325, "About 2 hours"),
        (86400, "Exactly 24 hours"),
        (90061, "Over 24 hours"),
        (172800, "Exactly 2 days"),
        (259200, "Exactly 3 days")
    ]
    
    print("NEW FORMAT EXAMPLES:")
    print("-" * 30)
    for seconds, description in test_cases:
        formatted = format_uptime(seconds)
        print(f"{description:20s} → {formatted}")
    
    print("\n" + "=" * 50)
    print("FORMAT RULES:")
    print("  • < 24 hours: hh:mm:ss")
    print("  • ≥ 24 hours: dd:hh:mm:ss")
    print("  • Always zero-padded (2 digits each)")
    print("  • No emojis, clean text only")
    
    print("\n" + "=" * 50)
    print("SYSTEM TRAY UPDATES:")
    print("  • Temperature: OK 45°C or WARM 78°C or HIGH 105°C")
    print("  • Load: OK 23% or WARM 78% or HIGH 100%")
    print("  • No emoji indicators, text only")
    
    print("\n" + "=" * 50)
    print("SYSTEM INFO DISPLAY:")
    print("  • PROCESS INFORMATION (no emoji)")
    print("  • Clean, professional appearance")
    print("  • Consistent text formatting")

if __name__ == "__main__":
    test_uptime_format()
