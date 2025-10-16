# 🎨 GUI Interface - Kick VOD 403 Fix

## Problem

When using the **Gradio GUI interface** with Kick VOD URLs, you were getting:
```
[https @ ...] HTTP error 403 Forbidden
Server returned 403 Forbidden (access denied)
```

The CLI mode was fixed, but the GUI wasn't updated.

## Solution

Updated `gradio_interface.py` to handle Kick VODs the same way as the CLI:

### Changes Made

1. **Added imports**:
   - `from kick_api import KickAPI`
   - `import config`

2. **Updated `__init__` method**:
   - Added `self.kick_api = KickAPI()`
   - Added `self.temp_vod_file = None`
   - Added `self.original_url = None`

3. **Updated `process_stream_wrapper` method**:
   - Detects if URL is a Kick VOD
   - Downloads VOD using yt-dlp with impersonation
   - Processes the downloaded file locally
   - Shows progress during download

4. **Updated `generate_clips_wrapper` method**:
   - Uses the downloaded VOD file for clip generation
   - Cleans up temp file after clips are generated

5. **Added `_cleanup_temp_vod` method**:
   - Automatically removes temporary VOD files

## How to Use the GUI

### 1. Launch the GUI

```bash
python main.py --gui
```

Or double-click `run.bat` (Windows)

### 2. Open in Browser

The interface will open at: `http://localhost:7860`

### 3. Enter Your Kick VOD URL

In the "Stream URL" field, paste:
```
https://kick.com/francovidalalcalde/videos/3a517d15-440e-4a67-86e5-486067c0f42a
```

Or any other Kick VOD URL in these formats:
- `https://kick.com/channel/videos/video-id`
- `https://kick.com/video/video-id`

### 4. Adjust Settings (Optional)

- **Clip Duration**: How long each clip should be (default: 30 seconds)
- **Min Gap**: Minimum time between highlights (default: 10 seconds)

### 5. Click "Analyze Stream"

**What happens:**
1. System detects it's a Kick VOD
2. Progress bar shows: "Detected Kick VOD - downloading..."
3. yt-dlp downloads the VOD (may take 2-10 minutes)
4. Progress bar updates: "Processing chunk X..."
5. Analysis completes and shows results

### 6. Review Results

You'll see:
- Number of audio highlights found
- Number of video highlights found
- Tables showing each highlight with timestamps and scores

### 7. Generate Clips

1. Select highlight type:
   - **Audio Only**: Only audio-based highlights
   - **Video Only**: Only video-based highlights
   - **Both**: All highlights

2. Click "Generate Clips"

3. Wait for clip generation (progress bar shows status)

4. Clips are saved to `output_clips/` folder

### 8. Download Clips

- Clips appear in the `output_clips/` folder
- You can also preview the first clip in the GUI

## What the GUI Shows

### During VOD Download:
```
Progress: Detected Kick VOD - downloading...
```

### During Processing:
```
Progress: Processing chunk 5 (150s / 3600s)
```

### After Analysis:
```
✅ Analysis Complete!

📊 Results:
- 🎵 Audio Highlights: 10
- 🎬 Video Highlights: 10
- ⏱️ Total Highlights: 20

🎯 Top Scores:
- Best Audio: 8.42
- Best Video: 12.35

💾 Ready to generate clips!
```

### After Clip Generation:
```
✅ Generated 20 clips!

📁 Clips saved to: output_clips/
- highlight_1_audio.mp4
- highlight_2_video.mp4
...

📊 Metadata: output_clips/highlights_20251012_204530.json
```

## Important Notes

### Download Time

- **First step takes longest**: Downloading the VOD (2-10 minutes)
- **Be patient**: The progress bar will update
- **Don't close the browser**: Keep the tab open during download

### Disk Space

- Ensure 5-10GB free space
- VOD is automatically deleted after clip generation

### Network Connection

- Stable internet required for download
- Wired connection recommended over WiFi

## Troubleshooting

### "Could not download Kick VOD"

**Possible causes:**
1. VOD was deleted or is private
2. Network issues
3. yt-dlp not installed or curl-cffi missing

**Solution:**
```bash
pip install yt-dlp curl-cffi
```

### "Already processing a stream"

The system can only process one stream at a time.

**Solution:** Wait for current processing to finish.

### GUI won't start

**Check if port is in use:**
```bash
# Try different port
python main.py --gui --port 8080
```

### Progress bar stuck

If download is taking very long:
- Check your internet connection
- Try a shorter VOD first
- Check if the VOD URL is valid

## Testing the Fix

### 1. Start GUI
```bash
python main.py --gui
```

### 2. Test with your VOD
Paste in GUI:
```
https://kick.com/francovidalalcalde/videos/3a517d15-440e-4a67-86e5-486067c0f42a
```

### 3. Click "Analyze Stream"

### 4. Watch Progress
- Should show "Detected Kick VOD - downloading..."
- Then "Processing chunk X..."
- Then show results

### 5. Generate Clips
- Select "Both"
- Click "Generate Clips"
- Check `output_clips/` folder

## Comparison: CLI vs GUI

### CLI Mode:
```bash
python main.py --url "KICK_VOD_URL" --generate-clips
```
- Faster for batch processing
- Better for automation
- Shows detailed logs
- No visual interface

### GUI Mode:
```bash
python main.py --gui
```
- Visual progress bars
- Interactive tables
- Preview clips
- Easier for beginners
- Better for single streams

## Advanced: Custom Port

If port 7860 is in use:

```bash
python main.py --gui --port 8080
```

Then open: `http://localhost:8080`

## Advanced: Public Access

To share the interface:

```bash
python main.py --gui --share
```

This creates a public Gradio link (valid for 72 hours).

## Files Modified

- **gradio_interface.py**: Added VOD download logic and cleanup

## Summary

✅ **Fixed**: GUI now handles Kick VODs with 403 errors  
✅ **Added**: VOD download with progress tracking  
✅ **Added**: Automatic cleanup of temporary files  
✅ **Improved**: Better error messages in GUI  

**Your GUI interface now works with Kick VODs!** 🎉

## Quick Reference

| Action | Command |
|--------|---------|
| Start GUI | `python main.py --gui` |
| Custom port | `python main.py --gui --port 8080` |
| Public link | `python main.py --gui --share` |
| CLI mode | `python main.py --url "URL" --generate-clips` |

## Next Steps

1. **Launch GUI**: `python main.py --gui`
2. **Paste your VOD URL** in the interface
3. **Click "Analyze Stream"** and wait
4. **Generate clips** from the results
5. **Find clips** in `output_clips/` folder

---

**The GUI is ready to use with Kick VODs!** 🚀
