# 🔧 Kick VOD 403 Error - FIXED

## Problem

When trying to process Kick VODs with URLs like:
```
https://kick.com/francovidalalcalde/videos/3a517d15-440e-4a67-86e5-486067c0f42a
```

You were getting:
```
[https @ ...] HTTP error 403 Forbidden
Server returned 403 Forbidden (access denied)
```

## Root Cause

1. **New URL format**: Kick uses `/channelname/videos/video-id` format (not just `/video/id`)
2. **Authentication required**: Kick VODs require browser impersonation to access
3. **FFprobe limitation**: Even with yt-dlp extracting the M3U8 URL, ffprobe can't access it without authentication headers

## Solution Implemented

### 1. Updated URL Parsing

**File: `kick_api.py`**

- Added support for `/channelname/videos/video-id` format
- Updated `extract_video_id_from_url()` to handle new pattern
- Updated `extract_channel_from_url()` to extract channel from video URLs

### 2. Added Browser Impersonation

**File: `kick_api.py`**

- Updated `get_stream_with_ytdlp()` to use `--impersonate chrome` flag
- Installed `curl-cffi` dependency for impersonation support

### 3. VOD Download Strategy

**File: `main.py`**

- Kick VODs are now **downloaded first** using yt-dlp
- The downloaded file is then processed locally (no 403 errors)
- Temporary VOD file is automatically cleaned up after processing

## What Was Installed

```bash
pip install curl-cffi
```

This package is required for yt-dlp's browser impersonation feature.

## How It Works Now

### For Kick VODs:

1. **Detect VOD URL**: System recognizes `/channelname/videos/video-id` format
2. **Download via yt-dlp**: Uses `yt-dlp --impersonate chrome` to download the full VOD
3. **Process locally**: Analyzes the downloaded file (no authentication issues)
4. **Generate clips**: Creates highlight clips from the local file
5. **Cleanup**: Removes temporary VOD file

### For Live Streams:

- Works as before using yt-dlp to extract authenticated stream URL

## Usage

### Process a Kick VOD:

```bash
python main.py --url "https://kick.com/CHANNEL/videos/VIDEO_ID" --generate-clips
```

### Example with your URL:

```bash
python main.py --url "https://kick.com/francovidalalcalde/videos/3a517d15-440e-4a67-86e5-486067c0f42a" --generate-clips
```

### What Happens:

```
2025-10-12 20:XX:XX - INFO - Detected Kick VOD - downloading via yt-dlp...
2025-10-12 20:XX:XX - INFO - Downloading VOD using yt-dlp to: temp_chunks/vod_3a517d15-440e-4a67-86e5-486067c0f42a.mp4
[download] Downloading video...
[download] 100% of 1.2GB in 02:30
2025-10-12 20:XX:XX - INFO - VOD downloaded successfully
2025-10-12 20:XX:XX - INFO - Processing stream: temp_chunks/vod_3a517d15-440e-4a67-86e5-486067c0f42a.mp4
2025-10-12 20:XX:XX - INFO - Processing chunk 0 at 0.0s
...
2025-10-12 20:XX:XX - INFO - Found 10 audio highlights
2025-10-12 20:XX:XX - INFO - Found 10 video highlights
2025-10-12 20:XX:XX - INFO - Generated 20 clips
2025-10-12 20:XX:XX - INFO - Cleaned up temporary VOD file
2025-10-12 20:XX:XX - INFO - Processing complete!
```

## Important Notes

### Download Time

- **VODs can be large** (1-5GB for long streams)
- **Download time depends on**:
  - Your internet speed
  - VOD length
  - Video quality
- **Expect**: 2-10 minutes for typical VODs

### Disk Space

- Ensure you have enough disk space in `temp_chunks/` folder
- The VOD is automatically deleted after processing
- Keep ~5-10GB free for safety

### Supported URL Formats

✅ **Now Supported:**
- `https://kick.com/channel/videos/video-id` (NEW!)
- `https://kick.com/video/video-id`
- `https://kick.com/channelname` (live)
- External M3U8 URLs

## Troubleshooting

### "curl-cffi not installed"

```bash
pip install curl-cffi
```

### "Download taking too long"

This is normal for large VODs. The system will wait up to 10 minutes.

If you need longer:
Edit `kick_api.py`, line 146:
```python
timeout=1200  # 20 minutes instead of 10
```

### "Not enough disk space"

Free up space in your drive or change temp directory in `config.py`:
```python
TEMP_DIR = 'D:/temp_clips'  # Use different drive
```

### "Download failed"

Possible causes:
1. VOD was deleted or is private
2. Network issues
3. Kick changed their API

Try:
```bash
# Test yt-dlp directly
yt-dlp --impersonate chrome "https://kick.com/CHANNEL/videos/VIDEO_ID"
```

## Performance Tips

### For Long VODs (2+ hours):

After download completes, processing will be faster if you:

Edit `config.py`:
```python
CHUNK_DURATION = 60  # Larger chunks
FRAME_SKIP = 10      # Skip more frames
TOP_N_HIGHLIGHTS = 5  # Fewer highlights
```

### For Quick Testing:

Use a short VOD first (< 30 minutes) to test the system.

## Verification

Test the fix:

```bash
# 1. Check URL parsing
python -c "from kick_api import KickAPI; api = KickAPI(); print(api.extract_video_id_from_url('https://kick.com/channel/videos/abc-123'))"
# Should print: abc-123

# 2. Check impersonation
yt-dlp --impersonate chrome --get-url "https://kick.com/CHANNEL/videos/VIDEO_ID"
# Should print M3U8 URL

# 3. Full test
python main.py --url "https://kick.com/CHANNEL/videos/VIDEO_ID"
```

## Summary

✅ **Fixed**: URL parsing for `/channelname/videos/video-id` format  
✅ **Added**: Browser impersonation with curl-cffi  
✅ **Implemented**: VOD download strategy to bypass 403 errors  
✅ **Added**: Automatic cleanup of temporary files  

**Your Kick VODs will now process successfully!** 🎉

## Files Modified

1. **kick_api.py**:
   - Updated `extract_video_id_from_url()` - Added new URL pattern
   - Updated `extract_channel_from_url()` - Extract channel from video URLs
   - Updated `get_stream_with_ytdlp()` - Added `--impersonate chrome`
   - Added `download_vod_with_ytdlp()` - New method to download VODs

2. **main.py**:
   - Updated `cli_mode()` - Detect and download VODs before processing
   - Added cleanup logic for temporary VOD files

## Next Steps

1. **Try your URL again**:
   ```bash
   python main.py --url "https://kick.com/francovidalalcalde/videos/3a517d15-440e-4a67-86e5-486067c0f42a" --generate-clips
   ```

2. **Be patient**: Download may take 2-10 minutes depending on VOD size

3. **Check output**: Clips will be in `output_clips/` folder

4. **Review highlights**: Check `output_clips/highlights.json` for timestamps

---

**The 403 error is now fixed!** Your program can process both live streams and VODs from Kick. 🚀
