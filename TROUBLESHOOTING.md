# 🔧 Troubleshooting Guide

## Quick Diagnostics

**Step 1: Run the system test**
```bash
python test_system.py
```

**Step 2: If you get ffprobe errors, run the FFmpeg diagnostic**
```bash
python diagnose_ffmpeg.py
```

These will identify most common issues automatically.

---

## Installation Issues

### ❌ Python Version Error

**Problem**: "Python 3.8 or higher is required"

**Solution**:
1. Check version: `python --version`
2. Download Python 3.8+ from https://python.org
3. During installation, check "Add Python to PATH"
4. Restart terminal/command prompt

### ❌ FFmpeg Not Found

**Problem**: "FFmpeg not found in PATH"

**Windows Solution**:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add `C:\ffmpeg\bin`
   - Click OK
4. Restart terminal
5. Test: `ffmpeg -version`

**Linux Solution**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS Solution**:
```bash
brew install ffmpeg
```

### ❌ Module Not Found

**Problem**: "ModuleNotFoundError: No module named 'gradio'"

**Solution**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install gradio numpy pandas opencv-python librosa scikit-learn requests moviepy ffmpeg-python soundfile scipy
```

**If pip is not found**:
```bash
python -m pip install -r requirements.txt
```

### ❌ Permission Denied

**Problem**: "Permission denied" when installing packages

**Windows Solution**:
```bash
pip install --user -r requirements.txt
```

**Linux/macOS Solution**:
```bash
pip install --user -r requirements.txt
# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

---

## Runtime Errors

### ❌ FFprobe Error

**Problem**: "ffprobe error (see stderr output for detail)" or "Failed to get stream info"

**This is the most common issue!**

**Quick Fix:**
```bash
python diagnose_ffmpeg.py
```

**Common Causes:**
1. **FFprobe not in PATH** - FFmpeg is installed but ffprobe isn't accessible
2. **Incomplete FFmpeg installation** - Only ffmpeg.exe installed, missing ffprobe.exe
3. **Stream URL issues** - URL requires authentication or is invalid
4. **Network issues** - Can't reach the stream

**Solutions:**

**1. Verify FFprobe Installation:**
```bash
ffprobe -version
```

If this fails, ffprobe is not installed or not in PATH.

**2. Reinstall FFmpeg Properly:**
- Download from: https://www.gyan.dev/ffmpeg/builds/
- Get "ffmpeg-release-essentials.zip"
- Extract to `C:\ffmpeg`
- Ensure `C:\ffmpeg\bin` contains:
  - ffmpeg.exe
  - ffprobe.exe
  - ffplay.exe
- Add `C:\ffmpeg\bin` to PATH
- **Restart terminal/IDE**

**3. Test with Local File:**
```bash
# Download a test video first
ffprobe test_video.mp4
```

**4. Check Stream URL:**
```bash
# Test if URL is accessible
ffprobe -v quiet -print_format json -show_format "your_stream_url"
```

**5. Use Diagnostic Tool:**
```bash
python diagnose_ffmpeg.py
```

This will identify the exact issue.

### ❌ 403 Forbidden Error (Kick Streams)

**Problem**: "HTTP error 403 Forbidden" when accessing Kick streams

**This is NORMAL for Kick.com streams!** They require authentication.

**Solution: Install yt-dlp**

```bash
pip install yt-dlp
```

**Why?**
- Kick streams are protected and require authentication
- yt-dlp handles authentication automatically
- Works with Kick, Twitch, YouTube, and many others

**Quick Fix:**
```bash
# 1. Install yt-dlp
pip install yt-dlp

# 2. Use channel URL (not direct stream URL)
python main.py --url "https://kick.com/channelname" --generate-clips
```

**Important:**
- ✅ Use: `https://kick.com/channelname`
- ❌ Don't use: `https://stream.kick.com/.../master.m3u8`

**See KICK_STREAMS_GUIDE.md for complete details**

### ❌ 403 Forbidden Error (Other Streams)

**Problem**: "403 error" when accessing non-Kick streams

**Automatic Handling**: The system automatically retries with:
- Exponential backoff (5 attempts)
- User agent rotation
- Different request headers

**If persists**:
1. Check if stream URL is valid
2. Try accessing URL in browser
3. Stream may require authentication (install yt-dlp)
4. Check if stream is geo-restricted

**Manual Fix**:
Edit `config.py`:
```python
MAX_RETRIES = 10  # Increase retries
BACKOFF_FACTOR = 3  # Longer wait times
```

### ❌ Stream URL Invalid

**Problem**: "Could not resolve Kick URL"

**Solution**:
1. Verify URL format:
   - ✅ `https://kick.com/channelname`
   - ✅ `https://example.com/stream.m3u8`
   - ❌ Invalid or incomplete URLs

2. Check if channel is live:
   ```python
   from kick_api import KickAPI
   api = KickAPI()
   metadata = api.get_stream_metadata('channelname')
   print(metadata)
   ```

3. For VODs, ensure video ID is correct

### ❌ Out of Memory

**Problem**: "MemoryError" or system freezes

**Solution**:
1. Close other applications
2. Reduce chunk duration in `config.py`:
   ```python
   CHUNK_DURATION = 20  # Reduce from 30
   ```

3. Increase frame skip:
   ```python
   FRAME_SKIP = 10  # Increase from 5
   ```

4. Process shorter streams first

### ❌ Slow Processing

**Problem**: Processing takes too long

**Solutions**:

**1. Optimize Frame Processing**:
```python
# In config.py
FRAME_SKIP = 10  # Process every 10th frame instead of 5th
```

**2. Reduce Chunk Overlap**:
```python
CHUNK_OVERLAP = 2  # Reduce from 5 seconds
```

**3. Disable Features** (advanced):
Edit `kick_clip_generator.py`:
```python
# In AudioAnalyzer
def extract_audio_features(self, video_path):
    # Comment out expensive features
    # tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    pass
```

**4. Check Internet Speed**:
- Slow download = slow processing
- Test with: `speedtest-cli`

### ❌ No Highlights Detected

**Problem**: Returns 0 highlights

**Solutions**:

**1. Lower Score Thresholds**:
```python
# In config.py
MIN_AUDIO_SCORE = 0.0  # Already at minimum
MIN_VIDEO_SCORE = 0.0  # Already at minimum
```

**2. Adjust Feature Weights**:
Edit `kick_clip_generator.py`:
```python
# In AudioAnalyzer.detect_audio_highlights()
score += features.get('rms_mean', 0) * 3.0  # Increase from 2.0
```

**3. Check Stream Quality**:
- Low-quality streams may not have clear features
- Test with high-quality stream first

**4. Verify Stream Has Audio/Video**:
```bash
ffmpeg -i "stream_url" 2>&1 | grep "Stream"
```

### ❌ FFmpeg Error

**Problem**: "FFmpeg error downloading chunk"

**Solutions**:

**1. Check FFmpeg Installation**:
```bash
ffmpeg -version
```

**2. Test Stream URL**:
```bash
ffmpeg -i "stream_url" -t 10 test.mp4
```

**3. Update FFmpeg**:
- Download latest version
- Replace old installation

**4. Check Stream Format**:
- Some formats may not be supported
- Try converting stream format

### ❌ Gradio Interface Won't Start

**Problem**: "Address already in use" or won't open

**Solutions**:

**1. Change Port**:
```bash
python main.py --gui --port 8080
```

**2. Kill Existing Process**:
```bash
# Windows
netstat -ano | findstr :7860
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:7860 | xargs kill -9
```

**3. Check Firewall**:
- Allow Python through firewall
- Allow port 7860

### ❌ Clips Not Generated

**Problem**: Analysis works but clips not created

**Solutions**:

**1. Check Output Directory**:
```bash
# Should exist and be writable
ls -la output_clips/
```

**2. Verify Disk Space**:
- Need space for clips
- Each clip ~50-100MB

**3. Check Permissions**:
```bash
# Windows
icacls output_clips
# Linux/macOS
chmod 755 output_clips/
```

**4. Check FFmpeg Copy Codec**:
- Some streams may need re-encoding
- Edit `kick_clip_generator.py`:
```python
stream = ffmpeg.output(stream, str(output_path),
                     vcodec='libx264',  # Re-encode instead of copy
                     acodec='aac',
                     loglevel='error')
```

---

## ML Model Issues

### ❌ Model Won't Load

**Problem**: "Failed to load model"

**Solution**:
1. Delete corrupted model:
   ```bash
   rm models/highlight_model.pkl
   ```

2. Model will be recreated automatically

### ❌ Model Not Improving

**Problem**: ML predictions not getting better

**Explanation**:
- Needs 10+ samples to train
- Improvement is gradual
- Check training data:

```python
from kick_clip_generator import MLHighlightModel
model = MLHighlightModel()
print(f"Audio samples: {len(model.training_data['audio']['features'])}")
print(f"Video samples: {len(model.training_data['video']['features'])}")
```

**Solution**:
- Process more streams (3-5 minimum)
- Ensure varied content
- Check if model is saving:
  ```bash
  ls -lh models/highlight_model.pkl
  ```

---

## Performance Issues

### 🐌 Very Slow Processing

**Diagnostic Checklist**:
- [ ] Internet speed (run speedtest)
- [ ] CPU usage (check task manager)
- [ ] Disk I/O (check disk activity)
- [ ] Memory usage (should be < 2GB)

**Optimization Steps**:

1. **Network Optimization**:
   ```python
   # In config.py
   REQUEST_TIMEOUT = 60  # Increase if slow connection
   ```

2. **CPU Optimization**:
   ```python
   FRAME_SKIP = 15  # Process fewer frames
   CHUNK_DURATION = 60  # Larger chunks, fewer requests
   ```

3. **Disk Optimization**:
   - Use SSD instead of HDD
   - Clear temp_chunks/ regularly
   - Ensure enough free space

### 💾 High Memory Usage

**Problem**: Using > 4GB RAM

**Solutions**:

1. **Reduce Chunk Size**:
   ```python
   CHUNK_DURATION = 15  # Smaller chunks
   ```

2. **Force Garbage Collection**:
   Add to `kick_clip_generator.py`:
   ```python
   import gc
   # After processing each chunk
   gc.collect()
   ```

3. **Limit Feature Extraction**:
   ```python
   # In VideoAnalyzer
   self.frame_skip = 10  # Increase from 5
   ```

---

## Platform-Specific Issues

### Windows

**Issue**: Path separators
```python
# Use Path from pathlib (already implemented)
from pathlib import Path
path = Path("output_clips") / "clip.mp4"
```

**Issue**: Long paths
- Enable long path support in Windows 10+
- Registry: `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled`

### Linux

**Issue**: Permission denied on directories
```bash
chmod -R 755 temp_chunks/ output_clips/ models/
```

**Issue**: FFmpeg not in PATH
```bash
export PATH=$PATH:/usr/local/bin
```

### macOS

**Issue**: SSL certificate errors
```bash
pip install --upgrade certifi
```

**Issue**: Permission denied
```bash
sudo chown -R $USER:staff output_clips/
```

---

## Debug Mode

### Enable Detailed Logging

Edit `config.py`:
```python
LOG_LEVEL = 'DEBUG'  # Change from 'INFO'
```

Or run with debug:
```bash
python -u main.py --url "stream_url" 2>&1 | tee debug.log
```

### Check Logs

```bash
# View recent errors
grep ERROR debug.log

# View warnings
grep WARNING debug.log

# View full processing
cat debug.log
```

---

## Getting Help

### Before Asking for Help

1. ✅ Run `python test_system.py`
2. ✅ Check this troubleshooting guide
3. ✅ Review error messages carefully
4. ✅ Test with simple example first
5. ✅ Check if issue is reproducible

### Information to Provide

When reporting issues, include:
- Python version: `python --version`
- FFmpeg version: `ffmpeg -version`
- Operating system
- Error message (full traceback)
- Steps to reproduce
- Stream URL (if public)
- Config changes made

### Common Error Patterns

**Pattern**: "Connection timeout"
→ **Cause**: Slow internet or server issues
→ **Fix**: Increase REQUEST_TIMEOUT

**Pattern**: "Codec not supported"
→ **Cause**: FFmpeg missing codec
→ **Fix**: Reinstall FFmpeg with full codecs

**Pattern**: "Index out of range"
→ **Cause**: Empty feature arrays
→ **Fix**: Check stream has audio/video

**Pattern**: "File not found"
→ **Cause**: Path issues or cleanup too early
→ **Fix**: Check directory permissions

---

## Testing Checklist

Before reporting a bug, test:

```bash
# 1. System test
python test_system.py

# 2. Simple example
python example_usage.py

# 3. Known good URL
python main.py --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --generate-clips

# 4. Check dependencies
pip list | grep -E "gradio|numpy|opencv|librosa|sklearn"

# 5. Check disk space
df -h

# 6. Check memory
free -h  # Linux
# Or Task Manager on Windows
```

---

## Emergency Fixes

### Nuclear Option: Fresh Start

```bash
# 1. Backup any custom changes
cp config.py config.py.backup

# 2. Clean everything
rm -rf temp_chunks/ output_clips/ models/
rm -rf __pycache__/

# 3. Reinstall dependencies
pip uninstall -y gradio numpy pandas opencv-python librosa scikit-learn
pip install -r requirements.txt

# 4. Test
python test_system.py
```

### Quick Fixes

```bash
# Fix: Stuck process
pkill -9 python

# Fix: Locked files
rm -rf temp_chunks/*

# Fix: Corrupted model
rm models/highlight_model.pkl

# Fix: Permission issues
chmod -R 755 .
```

---

## Still Having Issues?

1. **Check README.md** for detailed documentation
2. **Review ARCHITECTURE.md** to understand system
3. **Try example_usage.py** for working examples
4. **Simplify**: Test with minimal config
5. **Isolate**: Test each component separately

---

**Remember**: Most issues are related to:
1. FFmpeg installation (40%)
2. Python dependencies (30%)
3. Network/stream issues (20%)
4. Configuration (10%)

Run `python test_system.py` to diagnose automatically! 🔍
