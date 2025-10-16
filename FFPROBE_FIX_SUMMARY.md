# FFprobe Error - Fixes Applied

## Problem
You were experiencing persistent ffprobe errors when trying to analyze video streams:
```
ERROR - Failed to get stream info: ffprobe error (see stderr output for detail)
ERROR - Could not get stream info
```

## Root Causes

The error can occur due to several reasons:
1. **Invalid or inaccessible stream URLs**
2. **Network connectivity issues**
3. **Streams requiring authentication**
4. **Missing error details** (original code didn't show full error messages)

## Fixes Applied

### 1. Enhanced Error Handling (`kick_clip_generator.py`)

**Before:**
- Generic error messages
- No timeout handling
- Crashes on missing streams
- No fallback for missing audio

**After:**
- ✅ Detailed error messages with full stderr output
- ✅ 30-second timeout on probe operations
- ✅ Graceful handling of missing audio streams
- ✅ Safe defaults for missing metadata
- ✅ Better logging of stream information

**Key improvements:**
```python
# Added timeout
probe = ffmpeg.probe(stream_url, timeout=30)

# Safe stream detection
for stream in probe.get('streams', []):
    if stream.get('codec_type') == 'video' and not video_info:
        video_info = stream

# Detailed error logging
except ffmpeg.Error as e:
    error_msg = e.stderr.decode() if e.stderr else str(e)
    logger.error(f"FFprobe error: {error_msg}")
    logger.error(f"Stream URL: {stream_url}")
```

### 2. FFmpeg Verification (`kick_clip_generator.py`)

Added automatic verification that ffmpeg and ffprobe are available:

```python
def _verify_ffmpeg(self):
    """Verify ffmpeg and ffprobe are available"""
    # Checks both ffmpeg and ffprobe on initialization
    # Warns if not found in PATH
```

This runs when the StreamProcessor is initialized, alerting you immediately if there's a problem.

### 3. Diagnostic Tool (`diagnose_ffmpeg.py`)

Created a comprehensive diagnostic tool that checks:
- ✅ FFmpeg installation
- ✅ FFprobe installation
- ✅ PATH configuration
- ✅ Python ffmpeg-python library
- ✅ Actual probe functionality with test stream

**Usage:**
```bash
python diagnose_ffmpeg.py
```

### 4. Stream URL Tester (`test_stream_url.py`)

Created a tool to test specific stream URLs before processing:

**Usage:**
```bash
python test_stream_url.py "https://your-stream-url.m3u8"
```

**Features:**
- Tests if URL is accessible
- Shows stream information (resolution, duration, codecs)
- Provides detailed error messages
- Suggests solutions

### 5. Updated Documentation

**TROUBLESHOOTING.md:**
- Added dedicated FFprobe error section
- Step-by-step solutions
- Links to diagnostic tools

**Quick diagnostic steps:**
```bash
# Step 1: System test
python test_system.py

# Step 2: FFmpeg diagnostic
python diagnose_ffmpeg.py

# Step 3: Test your stream URL
python test_stream_url.py "your_url"
```

## How to Use

### If You're Getting FFprobe Errors:

**1. Run diagnostics:**
```bash
python diagnose_ffmpeg.py
```

**2. Test your stream URL:**
```bash
python test_stream_url.py "https://kick.com/channel"
```

**3. Check the detailed error message in logs**

The enhanced error handling now shows:
- Full ffprobe error output
- Stream URL being tested
- Specific failure reason

### Common Solutions

**Problem: "ffprobe not found"**
```bash
# Verify installation
ffprobe -version

# If not found, reinstall FFmpeg
# Download from: https://www.gyan.dev/ffmpeg/builds/
# Add C:\ffmpeg\bin to PATH
# Restart terminal
```

**Problem: "Connection timeout"**
```bash
# Check internet connection
# Try with local file first
python test_stream_url.py "C:\path\to\video.mp4"
```

**Problem: "No video stream found"**
- URL may be invalid
- Stream may be offline
- Authentication may be required

**Problem: "Protocol not supported"**
- Some stream formats may not be supported
- Try converting URL format
- Check if stream is accessible in browser

## Testing Your Fix

**1. Test with a known-good URL:**
```bash
python test_stream_url.py "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
```

**2. Test with your Kick stream:**
```bash
python test_stream_url.py "https://kick.com/your-channel"
```

**3. Run the full application:**
```bash
python main.py --gui
```

## What Changed in the Code

### File: `kick_clip_generator.py`

**Lines 118-183:** Complete rewrite of `get_stream_info()` method
- Added timeout parameter
- Safe stream detection with fallbacks
- Detailed error logging
- Graceful handling of missing audio
- Default values for live streams

**Lines 118-140:** New `_verify_ffmpeg()` method
- Checks ffmpeg availability on init
- Checks ffprobe availability on init
- Logs warnings if not found

### New Files Created

1. **diagnose_ffmpeg.py** - FFmpeg diagnostic tool
2. **test_stream_url.py** - Stream URL tester
3. **FFPROBE_FIX_SUMMARY.md** - This file

### Updated Files

1. **TROUBLESHOOTING.md** - Added FFprobe error section
2. **kick_clip_generator.py** - Enhanced error handling

## Expected Behavior Now

### Before Fix:
```
ERROR - Failed to get stream info: ffprobe error (see stderr output for detail)
ERROR - Could not get stream info
[No additional information]
```

### After Fix:
```
INFO - FFmpeg is available
INFO - FFprobe is available
INFO - Stream info: 1920x1080 @ 30.00fps, duration: 28800.0s
[Or detailed error with specific cause]
```

## Verification

Your diagnostic output shows:
- ✅ FFmpeg is installed and working
- ✅ FFprobe is installed and working  
- ✅ Python ffmpeg-python library is working
- ⚠️ Network test timed out (but library test passed)

**Conclusion:** Your FFmpeg setup is correct. The error is likely:
1. Invalid/inaccessible stream URL
2. Network connectivity to specific stream
3. Stream requiring authentication

**Next Steps:**
1. Use `test_stream_url.py` with your actual stream URL
2. Check the detailed error message
3. Verify stream is accessible in browser/VLC
4. Try with a local video file first to confirm system works

## Support

If issues persist:
1. Run: `python diagnose_ffmpeg.py` and share output
2. Run: `python test_stream_url.py "your_url"` and share output
3. Check TROUBLESHOOTING.md for specific error messages
4. Verify stream URL is accessible in VLC Media Player

---

**Summary:** The code now has much better error handling and diagnostic tools to help identify the exact cause of ffprobe errors. The issue is most likely with the stream URL itself rather than your FFmpeg installation.
