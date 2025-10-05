# Troubleshooting Guide - Screenshot & System Control

## Current Issues

### 1. Screenshot Not Actually Saving Files ❌

**Problem**: The screenshot agent returns success but doesn't actually capture/save screenshots.

**Root Cause**: PowerShell script execution policy or System.Drawing assembly not loading properly.

**How to Test**:
```powershell
# Open PowerShell as Administrator and run:
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bitmap.Save("C:\Users\SURAJ\Pictures\test_screenshot.png", [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
```

**Solutions**:

#### Option 1: Use Alternative Windows Screenshot Method (RECOMMENDED)
Instead of PowerShell, use Python libraries:

```bash
# Install Python screenshot library
pip install pillow mss
```

Then modify screenshot_agent.py to use Python-based screenshot.

#### Option 2: Enable PowerShell Execution Policy
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Option 3: Use Windows Snipping Tool (Fallback - Manual)
Already implemented in the code but opens Snipping Tool manually.

---

### 2. Volume Control Not Working ❌

**Problem**: System control returns success but volume doesn't change.

**Root Cause**: Windows SendKeys doesn't work reliably for volume control via PowerShell subprocess.

**How to Test**:
```powershell
# This won't work from subprocess:
powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"

# Better approach - use nircmd or pycaw
```

**Solutions**:

#### Option 1: Use Python Audio Control Library (RECOMMENDED)
```bash
# Install pycaw for Windows audio control
pip install pycaw comtypes
```

Then use Python to control volume directly.

#### Option 2: Use NirCmd (Free Windows Utility)
```bash
# Download NirCmd from: https://www.nirsoft.net/utils/nircmd.html
# Place nircmd.exe in C:\Windows\System32\

# Then commands become:
nircmd.exe changesysvolume 5000   # Increase volume
nircmd.exe changesysvolume -5000  # Decrease volume
nircmd.exe mutesysvolume 1        # Mute
nircmd.exe mutesysvolume 0        # Unmute
```

---

### 3. Multi-Task Not Parsing Correctly ⚠️

**Problem**: "take screenshot and send to Jay" only detects screenshot task, not the send task.

**Root Cause**: Regex pattern matching not catching "send it to" pattern.

**Current Detection**:
```
[WORKFLOW] Starting 1-task workflow:
  Task 1: screenshot - take screenshot
```

**Expected**:
```
[WORKFLOW] Starting 2-task workflow:
  Task 1: screenshot - take screenshot
  Task 2: whatsapp/email - send to Jay
```

**Solution**: Fix regex patterns in `multi_task_orchestrator.py`

---

## Quick Fix Implementation

I'll create updated versions with working implementations:

### Fix 1: Python-Based Screenshot (Works Immediately)

```python
# Using pillow + mss (fast, reliable)
from mss import mss
from PIL import Image

def capture_screenshot_python(path):
    with mss() as sct:
        # Capture entire screen
        monitor = sct.monitors[1]  # Primary monitor
        screenshot = sct.grab(monitor)
        
        # Convert to PIL Image and save
        img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
        img.save(path, 'PNG')
    return path
```

### Fix 2: Python-Based Volume Control (Windows)

```python
# Using pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def change_volume(change_percent):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = min(1.0, max(0.0, current + (change_percent / 100)))
    volume.SetMasterVolumeLevelScalar(new_volume, None)
```

---

## Current Working Features ✅

Based on logs, these ARE working:

1. ✅ **AI Enhancement** - All commands enhanced by Groq AI
2. ✅ **File Search** - Found apple.pdf successfully
3. ✅ **WhatsApp** - Parsed "send WhatsApp to Jay" correctly
4. ✅ **Intent Detection** - All agents routing correctly
5. ✅ **Multi-task Detection** - Detects workflow (but parsing needs fix)

---

## Recommended Next Steps

### Immediate Fixes (Do These Now):

1. **Install Required Libraries**:
```bash
cd backend
pip install pillow mss pycaw comtypes
```

2. **Update screenshot_agent.py** with Python-based screenshot
3. **Update system_control_agent.py** with pycaw for volume
4. **Fix multi_task_orchestrator.py** regex patterns

### Test Commands:

After fixes, test these:

```
✅ Working Now:
- "find apple.pdf" 
- "send whatsapp to Jay"
- "open apple PDF from file"

⚠️ Need Fixes:
- "screenshot" (need Python screenshot)
- "volume up" (need pycaw)
- "take screenshot and send to Jay" (need regex fix)
```

---

## Manual Workarounds (Until Fixed)

### For Screenshots:
Use Windows built-in shortcuts:
- `Win + Shift + S` - Snipping Tool
- `Win + PrintScreen` - Save to Pictures/Screenshots
- `PrintScreen` - Copy to clipboard

### For Volume:
- Use physical volume buttons
- Click volume icon in taskbar
- Use `Win + X` → Volume Mixer

### For Multi-Task:
Do tasks separately:
1. "take screenshot"
2. Then "send to Jay via WhatsApp"

---

## Detailed Error Analysis

### Screenshot Error Analysis:

```python
# Current code tries PowerShell:
ps_script = """
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
...
"""
result = subprocess.run(['powershell', '-Command', ps_script], ...)
```

**Problem**: 
- PowerShell subprocess doesn't inherit GUI context
- System.Drawing may not load in subprocess
- No error output captured

**Fix**: Use Python native screenshot

### Volume Error Analysis:

```python
# Current code:
"volume_up": {
    "windows": "powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]175)\""
}
```

**Problem**:
- SendKeys requires active window
- Subprocess has no GUI context
- VBS keys don't work in background

**Fix**: Use direct Windows Audio API via pycaw

---

## Implementation Priority

### Priority 1 - Critical (Fix Now):
1. Screenshot with Python (mss + pillow)
2. Volume control with pycaw
3. Multi-task regex patterns

### Priority 2 - Enhancement:
1. Error logging from screenshot/volume
2. Retry logic
3. User feedback messages

### Priority 3 - Nice to Have:
1. Screenshot region selection
2. Volume percentage control
3. Complex multi-task workflows

---

## Testing Checklist

After implementing fixes:

### Screenshot:
- [ ] "screenshot" - saves to Pictures/Screenshots
- [ ] File exists after command
- [ ] Can open saved screenshot
- [ ] Multi-monitor support

### Volume:
- [ ] "volume up" - increases by 10%
- [ ] "volume down" - decreases by 10%
- [ ] "mute" - mutes audio
- [ ] "unmute" - unmutes audio
- [ ] Actual system volume changes

### Multi-Task:
- [ ] "take screenshot and send to Jay" - 2 tasks
- [ ] "find apple.pdf and send to Jay" - 2 tasks
- [ ] Both tasks execute in sequence
- [ ] Data passes between tasks

---

## Next Steps

**I can create fixed versions of these files for you with:**
1. Python-based screenshot (using mss + pillow)
2. Python-based volume control (using pycaw)
3. Fixed multi-task regex patterns
4. Better error logging

**Would you like me to:**
- A) Create the fixed versions now?
- B) Just install the libraries and I'll update the code?
- C) Provide step-by-step manual fixes?

Let me know and I'll implement the fixes! 🚀
