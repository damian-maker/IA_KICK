# 🎮 Kick Streams - Complete Guide

## The 403 Forbidden Issue

Kick.com streams are **protected** and require proper authentication to access. When you try to access a Kick stream URL directly, you'll get:

```
HTTP error 403 Forbidden
Server returned 403 Forbidden (access denied)
```

This is **normal and expected** - Kick protects their streams from direct access.

## Solution: yt-dlp

**yt-dlp** is a powerful tool that handles authentication for protected streams, including Kick.com.

### Installation

```bash
pip install yt-dlp
```

That's it! The application will automatically use yt-dlp when processing Kick URLs.

### How It Works

1. You provide a Kick channel URL: `https://kick.com/channelname`
2. The application detects it's a Kick URL
3. yt-dlp extracts the authenticated stream URL
4. The application processes the stream normally

### Supported URL Formats

✅ **Kick Channel URL** (Recommended):
```
https://kick.com/channelname
```

✅ **Kick Video URL**:
```
https://kick.com/video/12345
```

❌ **Direct Stream URL** (Won't work):
```
https://stream.kick.com/ivs/v1/.../master.m3u8
```
*These require the original page URL for authentication*

## Quick Start

### 1. Install yt-dlp

```bash
pip install yt-dlp
```

### 2. Verify Installation

```bash
yt-dlp --version
```

Should show version number (e.g., `2024.10.07`)

### 3. Test with a Kick Stream

```bash
python test_stream_url.py "https://kick.com/channelname"
```

### 4. Process the Stream

**GUI Mode:**
```bash
python main.py --gui
```
Enter the Kick channel URL in the interface.

**CLI Mode:**
```bash
python main.py --url "https://kick.com/channelname" --generate-clips
```

## Troubleshooting

### ❌ "yt-dlp not found"

**Problem**: yt-dlp is not installed

**Solution**:
```bash
pip install yt-dlp
```

Verify:
```bash
yt-dlp --version
```

### ❌ "Direct stream URLs from Kick require the original page URL"

**Problem**: You're using a direct `.m3u8` URL instead of the channel URL

**Solution**: Use the channel URL instead:
- ❌ `https://stream.kick.com/.../master.m3u8`
- ✅ `https://kick.com/channelname`

### ❌ "Channel is not currently live"

**Problem**: The channel is offline

**Solution**:
- Check if the channel is actually streaming
- Try a different channel that's currently live
- For VODs, use the video URL format

### ❌ "yt-dlp extraction failed"

**Problem**: yt-dlp couldn't extract the stream

**Possible causes**:
1. Channel is offline
2. Stream is geo-restricted
3. Kick changed their format
4. Network issues

**Solutions**:
```bash
# Test yt-dlp directly
yt-dlp -F "https://kick.com/channelname"

# Update yt-dlp
pip install --upgrade yt-dlp

# Check if stream works in browser
# Open the Kick URL in your browser
```

## Advanced Usage

### Check Stream Info with yt-dlp

```bash
# List available formats
yt-dlp -F "https://kick.com/channelname"

# Get JSON info
yt-dlp -j "https://kick.com/channelname"

# Download a clip manually
yt-dlp "https://kick.com/channelname"
```

### Using with Other Platforms

yt-dlp supports many platforms:
- ✅ Kick.com
- ✅ Twitch.tv
- ✅ YouTube
- ✅ Many others

Just use the channel URL and the application will handle it!

## Why yt-dlp?

### Without yt-dlp:
```
Kick URL → Direct stream URL → 403 Forbidden ❌
```

### With yt-dlp:
```
Kick URL → yt-dlp extracts authenticated URL → Success ✅
```

yt-dlp:
- Handles cookies and authentication
- Bypasses geo-restrictions (when possible)
- Supports hundreds of platforms
- Regularly updated for platform changes
- Open source and well-maintained

## Example Workflow

### Processing a Live Kick Stream

```bash
# 1. Find a live Kick channel
# Visit https://kick.com and find a live stream

# 2. Copy the channel URL
# Example: https://kick.com/xqc

# 3. Test the URL
python test_stream_url.py "https://kick.com/xqc"

# 4. Process the stream
python main.py --url "https://kick.com/xqc" --generate-clips

# 5. Check output
# Clips will be in output_clips/
```

### Processing a Kick VOD

```bash
# 1. Find a Kick video
# Example: https://kick.com/video/abc123

# 2. Process it
python main.py --url "https://kick.com/video/abc123" --generate-clips
```

## Performance Notes

### With yt-dlp:
- **Initial extraction**: 5-10 seconds
- **Processing**: Same as before
- **Total overhead**: Minimal (~10 seconds)

### Benefits:
- ✅ Works with protected streams
- ✅ Handles authentication automatically
- ✅ Supports multiple platforms
- ✅ Regularly updated

## Alternative: Local Files

If you already have a downloaded video:

```bash
python main.py --url "C:\path\to\video.mp4" --generate-clips
```

No yt-dlp needed for local files!

## FAQ

**Q: Do I need yt-dlp for all streams?**  
A: Only for protected streams (Kick, Twitch, etc.). Public URLs work without it.

**Q: Is yt-dlp safe?**  
A: Yes! It's open source and widely used. GitHub: https://github.com/yt-dlp/yt-dlp

**Q: Will yt-dlp download the entire stream?**  
A: No! The application still uses chunked processing. yt-dlp only extracts the authenticated URL.

**Q: What if yt-dlp fails?**  
A: The application will try the API method as fallback, but it may not work for protected streams.

**Q: Can I use this with Twitch?**  
A: Yes! yt-dlp supports Twitch too:
```bash
python main.py --url "https://twitch.tv/channelname" --generate-clips
```

**Q: Do I need a Kick account?**  
A: No! yt-dlp handles authentication automatically.

## Summary

### For Kick Streams:

1. **Install yt-dlp**: `pip install yt-dlp`
2. **Use channel URL**: `https://kick.com/channelname`
3. **Process normally**: Application handles the rest

### Error Messages Explained:

- **"403 Forbidden"** → Install yt-dlp
- **"yt-dlp not found"** → Run `pip install yt-dlp`
- **"Channel not live"** → Stream is offline
- **"Direct stream URLs require page URL"** → Use channel URL instead

---

**Ready to process Kick streams!** 🎮

Install yt-dlp and you're all set:
```bash
pip install yt-dlp
python main.py --gui
```
