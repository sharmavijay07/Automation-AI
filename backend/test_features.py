"""
Test script for new features: Screenshot, System Control, Multi-task
Run this to verify all packages are installed and working
"""

import sys
from pathlib import Path

print("=" * 60)
print("🧪 TESTING VAANI NEW FEATURES")
print("=" * 60)

# Test 1: PIL (Screenshot)
print("\n1️⃣ Testing PIL (Screenshot feature)...")
try:
    from PIL import ImageGrab
    print("   ✅ PIL ImageGrab imported successfully!")
    
    # Try to capture a test screenshot
    try:
        screenshot = ImageGrab.grab()
        test_path = Path.home() / "Pictures" / "test_vaani_screenshot.png"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot.save(str(test_path), 'PNG')
        
        if test_path.exists():
            size_kb = test_path.stat().st_size / 1024
            print(f"   ✅ Test screenshot saved: {test_path}")
            print(f"   📊 Size: {size_kb:.2f} KB")
            test_path.unlink()  # Delete test file
        else:
            print(f"   ❌ Screenshot not saved to {test_path}")
    except Exception as e:
        print(f"   ❌ Screenshot capture failed: {e}")
        
except ImportError as e:
    print(f"   ❌ PIL not installed: {e}")
    print(f"   💡 Run: pip install pillow")

# Test 2: pycaw (Volume Control)
print("\n2️⃣ Testing pycaw (Volume Control feature)...")
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    print("   ✅ pycaw imported successfully!")
    
    # Try to get volume interface
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = volume.GetMasterVolumeLevelScalar()
        print(f"   ✅ Volume control working! Current volume: {int(current_volume * 100)}%")
    except Exception as e:
        print(f"   ❌ Volume control failed: {e}")
        
except ImportError as e:
    print(f"   ❌ pycaw not installed: {e}")
    print(f"   💡 Run: pip install pycaw comtypes")

# Test 3: psutil (Battery Info)
print("\n3️⃣ Testing psutil (Battery feature)...")
try:
    import psutil
    print("   ✅ psutil imported successfully!")
    
    try:
        battery = psutil.sensors_battery()
        if battery:
            print(f"   ✅ Battery: {battery.percent}% ({'Charging' if battery.power_plugged else 'Discharging'})")
        else:
            print(f"   ℹ️  No battery detected (desktop PC?)")
    except Exception as e:
        print(f"   ❌ Battery check failed: {e}")
        
except ImportError as e:
    print(f"   ❌ psutil not installed: {e}")
    print(f"   💡 Run: pip install psutil")

# Test 4: screen-brightness-control (Brightness)
print("\n4️⃣ Testing screen-brightness-control (Brightness feature)...")
try:
    import screen_brightness_control as sbc
    print("   ✅ screen-brightness-control imported successfully!")
    
    try:
        brightness = sbc.get_brightness()
        print(f"   ✅ Brightness control working! Current: {brightness[0]}%")
    except Exception as e:
        print(f"   ❌ Brightness control failed: {e}")
        print(f"   ℹ️  Note: Brightness control may not work on all monitors")
        
except ImportError as e:
    print(f"   ❌ screen-brightness-control not installed: {e}")
    print(f"   💡 Run: pip install screen-brightness-control")

# Test 5: datetime (Time feature)
print("\n5️⃣ Testing datetime (Time feature)...")
try:
    from datetime import datetime
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    print(f"   ✅ Current time: {time_str}")
    print(f"   ✅ Current date: {date_str}")
except Exception as e:
    print(f"   ❌ Datetime failed: {e}")

print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("If all tests passed ✅, your features are ready!")
print("If any failed ❌, install the missing packages:")
print("   pip install pillow pycaw comtypes psutil screen-brightness-control")
print("=" * 60)
