# 🚀 Quick Reference Guide

## One-Line Commands

### Live Streams
```bash
# Basic
python main.py --url "https://kick.com/channelname" --generate-clips

# Custom duration
python main.py --url "https://kick.com/channelname" --clip-duration 45 --generate-clips

# Audio only
python main.py --url "https://kick.com/channelname" --type audio --generate-clips

# Video only
python main.py --url "https://kick.com/channelname" --type video --generate-clips
```

### Past Streams (VODs)
```bash
# Basic
python main.py --url "https://kick.com/video/VIDEO_ID" --generate-clips

# Custom settings
python main.py --url "https://kick.com/video/VIDEO_ID" --clip-duration 60 --min-gap 20 --generate-clips
```

### GUI Mode
```bash
# Launch interface
python main.py --gui

# Custom port
python main.py --gui --port 8080

# Public link
python main.py --gui --share
```

---

## URL Formats

### ✅ Supported URLs

| Type | Format | Example |
|------|--------|---------|
| Kick Live | `https://kick.com/CHANNEL` | `https://kick.com/xqc` |
| Kick VOD | `https://kick.com/video/VIDEO_ID` | `https://kick.com/video/abc123-def` |
| Direct M3U8 | `https://example.com/stream.m3u8` | Any valid M3U8 URL |
| Twitch | `https://twitch.tv/CHANNEL` | Requires yt-dlp |
| YouTube | `https://youtube.com/watch?v=ID` | Requires yt-dlp |

### ❌ Not Supported

- Direct Kick stream URLs (use channel URL instead)
- Expired VOD links
- Private/subscriber-only streams

---

## Command-Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--url` | Stream URL (required for CLI) | - | `--url "https://kick.com/channel"` |
| `--clip-duration` | Clip length in seconds | 30 | `--clip-duration 45` |
| `--min-gap` | Min seconds between highlights | 10 | `--min-gap 15` |
| `--generate-clips` | Generate video clips | False | `--generate-clips` |
| `--type` | Highlight type | both | `--type audio` |
| `--gui` | Launch GUI mode | False | `--gui` |
| `--port` | GUI server port | 7860 | `--port 8080` |
| `--share` | Create public link | False | `--share` |

---

## Configuration Quick Tweaks

Edit `config.py`:

### Faster Processing
```python
CHUNK_DURATION = 60
FRAME_SKIP = 15
TOP_N_HIGHLIGHTS = 5
```

### Better Quality
```python
CHUNK_DURATION = 20
FRAME_SKIP = 3
TOP_N_HIGHLIGHTS = 15
```

### More Highlights
```python
MIN_GAP_BETWEEN_HIGHLIGHTS = 5
TOP_N_HIGHLIGHTS = 20
```

### Fewer Highlights
```python
MIN_GAP_BETWEEN_HIGHLIGHTS = 30
TOP_N_HIGHLIGHTS = 5
```

---

## Output Files

| File | Location | Description |
|------|----------|-------------|
| Clips | `output_clips/clip_N_TYPE.mp4` | Generated video clips |
| Metadata | `output_clips/highlights.json` | Highlight timestamps & scores |
| Temp | `temp_chunks/*.mp4` | Temporary files (auto-deleted) |
| Model | `models/highlight_model.pkl` | ML model (improves over time) |

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| FFmpeg not found | Add to PATH, restart terminal |
| FFprobe error | Run `python diagnose_ffmpeg.py` |
| 403 Forbidden | Install yt-dlp: `pip install yt-dlp` |
| No highlights | Use `--min-gap 5` or `--type both` |
| Slow processing | Increase `FRAME_SKIP` in config.py |
| Out of memory | Reduce `CHUNK_DURATION` in config.py |
| Port in use | Use `--port 8080` |

---

## Python API Quick Start

```python
from kick_clip_generator import KickClipGenerator
from kick_api import KickAPI

# Initialize
generator = KickClipGenerator(clip_duration=30, min_gap=10)
api = KickAPI()

# Resolve URL
url = "https://kick.com/channelname"
stream_url = api.resolve_kick_url(url)

# Process stream
audio_hl, video_hl = generator.process_stream(stream_url)

# Generate clips
clips = generator.generate_clips(stream_url, audio_hl + video_hl)

print(f"Generated {len(clips)} clips")
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8+ | 3.10+ |
| RAM | 4GB | 8GB+ |
| Disk Space | 2GB | 10GB+ |
| Internet | 10 Mbps | 50 Mbps+ |
| FFmpeg | Any version | Latest |

---

## Installation Quick Check

```bash
# Check Python
python --version  # Should be 3.8+

# Check FFmpeg
ffmpeg -version
ffprobe -version

# Check dependencies
pip list | grep -E "gradio|numpy|opencv|librosa"

# Run system test
python test_system.py
```

---

## Common Workflows

### 1. Quick Clip Generation
```bash
python main.py --url "URL" --generate-clips
```

### 2. Analysis First, Clips Later
```bash
# Step 1: Analyze
python main.py --url "URL"

# Step 2: Review highlights.json
cat output_clips/highlights.json

# Step 3: Generate if satisfied
python main.py --url "URL" --generate-clips
```

### 3. Batch Processing
```bash
for url in $(cat urls.txt); do
  python main.py --url "$url" --generate-clips
done
```

---

## Performance Tips

1. **Use yt-dlp**: `pip install yt-dlp`
2. **Close other apps**: Free up RAM
3. **Use SSD**: Faster disk I/O
4. **Wired connection**: More stable than WiFi
5. **Process shorter streams first**: Test before long streams

---

## Getting Help

1. **System test**: `python test_system.py`
2. **FFmpeg diagnostic**: `python diagnose_ffmpeg.py`
3. **Troubleshooting guide**: `TROUBLESHOOTING.md`
4. **Usage examples**: `USAGE_EXAMPLES.md`
5. **Enable debug**: Set `LOG_LEVEL = 'DEBUG'` in config.py

---

## Links

- **Installation**: `README.md`
- **Architecture**: `ARCHITECTURE.md`
- **Kick Streams**: `KICK_STREAMS_GUIDE.md`
- **GUI Guide**: `INTERFACE_GUIDE.md`
- **Examples**: `USAGE_EXAMPLES.md`

---

**Need more help? Check the full documentation!** 📚
