# 📖 Usage Examples - Live and Past Streams

This guide shows you how to generate clips from both **live streams** and **past streams (VODs)** on Kick.

---

## 🎯 Quick Start

### For Live Streams

```bash
# Process a live Kick stream
python main.py --url "https://kick.com/channelname" --generate-clips

# Or use the GUI
python main.py --gui
```

### For Past Streams (VODs)

```bash
# Process a Kick VOD using video ID
python main.py --url "https://kick.com/video/abc123-def456-789" --generate-clips

# Or use the GUI and paste the VOD URL
python main.py --gui
```

---

## 🔴 Live Stream Examples

### Example 1: Basic Live Stream Processing

```bash
python main.py --url "https://kick.com/xqc" --generate-clips
```

**What happens:**
1. Connects to the live stream
2. Analyzes audio and video in real-time
3. Detects highlights automatically
4. Generates clips from the best moments

### Example 2: Custom Clip Duration

```bash
python main.py --url "https://kick.com/channelname" \
  --clip-duration 45 \
  --min-gap 20 \
  --generate-clips
```

**Parameters:**
- `--clip-duration 45`: Each clip will be 45 seconds long
- `--min-gap 20`: At least 20 seconds between highlights

### Example 3: Audio-Only Highlights

```bash
python main.py --url "https://kick.com/channelname" \
  --type audio \
  --generate-clips
```

**Use case:** Perfect for streams where audio reactions are more important than visual action.

### Example 4: Video-Only Highlights

```bash
python main.py --url "https://kick.com/channelname" \
  --type video \
  --generate-clips
```

**Use case:** Great for gameplay streams where visual action matters most.

---

## 📼 Past Stream (VOD) Examples

### Example 1: Process a VOD

```bash
python main.py --url "https://kick.com/video/abc123-def456-789" --generate-clips
```

**What happens:**
1. Downloads the VOD in chunks
2. Analyzes the entire video
3. Finds the best moments
4. Creates highlight clips

### Example 2: VOD with Custom Settings

```bash
python main.py --url "https://kick.com/video/abc123-def456-789" \
  --clip-duration 60 \
  --type both \
  --generate-clips
```

**Result:** 60-second clips combining both audio and video highlights.

### Example 3: Quick Analysis (No Clips)

```bash
python main.py --url "https://kick.com/video/abc123-def456-789"
```

**Result:** Shows highlight timestamps without generating clips (faster).

---

## 🖥️ GUI Mode (Recommended for Beginners)

### Launch the GUI

```bash
python main.py --gui
```

Or use the quick start script:
```bash
run.bat
```

### Using the GUI

1. **Paste URL**: Enter either a live stream or VOD URL
2. **Adjust Settings**: 
   - Clip Duration (default: 30s)
   - Minimum Gap (default: 10s)
   - Highlight Type (audio/video/both)
3. **Click "Process Stream"**
4. **Wait for Analysis**
5. **Download Clips** from the output folder

**Supported URLs:**
- ✅ `https://kick.com/channelname` (live)
- ✅ `https://kick.com/video/video-id` (VOD)
- ✅ `https://example.com/stream.m3u8` (external)

---

## 🔧 Advanced Usage

### Batch Processing Multiple Streams

Create a script `batch_process.py`:

```python
from kick_clip_generator import KickClipGenerator
from kick_api import KickAPI

generator = KickClipGenerator(clip_duration=30, min_gap=10)
api = KickAPI()

# List of streams to process
streams = [
    "https://kick.com/channelname1",
    "https://kick.com/video/vod-id-1",
    "https://kick.com/channelname2",
    "https://kick.com/video/vod-id-2",
]

for stream_url in streams:
    print(f"\n{'='*60}")
    print(f"Processing: {stream_url}")
    print('='*60)
    
    # Resolve URL
    resolved_url = api.resolve_kick_url(stream_url)
    if not resolved_url:
        print(f"Failed to resolve: {stream_url}")
        continue
    
    # Process stream
    audio_highlights, video_highlights = generator.process_stream(resolved_url)
    
    # Generate clips
    all_highlights = audio_highlights + video_highlights
    clips = generator.generate_clips(resolved_url, all_highlights)
    
    print(f"Generated {len(clips)} clips")
```

Run it:
```bash
python batch_process.py
```

### Custom Highlight Detection

Edit `config.py` to adjust detection sensitivity:

```python
# Make detection more sensitive (more highlights)
MIN_GAP_BETWEEN_HIGHLIGHTS = 5  # Reduce from 10
TOP_N_HIGHLIGHTS = 20  # Increase from 10

# Make detection less sensitive (fewer, better highlights)
MIN_GAP_BETWEEN_HIGHLIGHTS = 30  # Increase from 10
TOP_N_HIGHLIGHTS = 5  # Reduce from 10
```

### Export Highlight Timestamps

```python
from kick_clip_generator import KickClipGenerator
from kick_api import KickAPI
import json

generator = KickClipGenerator()
api = KickAPI()

stream_url = "https://kick.com/channelname"
resolved_url = api.resolve_kick_url(stream_url)

audio_highlights, video_highlights = generator.process_stream(resolved_url)

# Export to JSON
generator.export_highlights_json(
    audio_highlights, 
    video_highlights, 
    'highlights.json'
)

# Read and display
with open('highlights.json', 'r') as f:
    data = json.load(f)
    
print("Audio Highlights:")
for h in data['audio_highlights']:
    print(f"  {h['start_time']:.1f}s - Score: {h['score']:.2f}")

print("\nVideo Highlights:")
for h in data['video_highlights']:
    print(f"  {h['start_time']:.1f}s - Score: {h['score']:.2f}")
```

---

## 🎮 Platform-Specific Examples

### Kick.com (Recommended: Use yt-dlp)

**Install yt-dlp first:**
```bash
pip install yt-dlp
```

**Live Stream:**
```bash
python main.py --url "https://kick.com/xqc" --generate-clips
```

**VOD:**
```bash
python main.py --url "https://kick.com/video/abc123-def456" --generate-clips
```

### Twitch (via yt-dlp)

```bash
python main.py --url "https://twitch.tv/channelname" --generate-clips
```

### YouTube Live

```bash
python main.py --url "https://youtube.com/watch?v=VIDEO_ID" --generate-clips
```

### Direct M3U8 Streams

```bash
python main.py --url "https://example.com/stream/master.m3u8" --generate-clips
```

---

## 📊 Understanding Output

### Output Directory Structure

```
output_clips/
├── clip_1_audio.mp4    # Audio highlight #1
├── clip_2_video.mp4    # Video highlight #2
├── clip_3_audio.mp4    # Audio highlight #3
└── highlights.json     # Metadata file
```

### Highlights JSON Format

```json
{
  "audio_highlights": [
    {
      "start_time": 125.5,
      "end_time": 155.5,
      "score": 8.42,
      "type": "audio",
      "features": {...},
      "timestamp": "2025-10-12T20:15:30"
    }
  ],
  "video_highlights": [...],
  "generated_at": "2025-10-12T20:15:30"
}
```

---

## ⚙️ Performance Optimization

### For Long Streams (2+ hours)

```python
# In config.py
CHUNK_DURATION = 60  # Larger chunks = faster processing
FRAME_SKIP = 10      # Skip more frames = faster processing
TOP_N_HIGHLIGHTS = 5  # Fewer highlights = faster generation
```

### For High-Quality Analysis

```python
# In config.py
CHUNK_DURATION = 20  # Smaller chunks = more precise
FRAME_SKIP = 3       # Process more frames = better detection
TOP_N_HIGHLIGHTS = 15 # More highlights
```

### For Low-End Systems

```python
# In config.py
CHUNK_DURATION = 30
FRAME_SKIP = 15      # Skip many frames
TOP_N_HIGHLIGHTS = 5
```

---

## 🐛 Common Issues

### Issue: "Could not resolve Kick URL"

**Solution:** Install yt-dlp
```bash
pip install yt-dlp
```

### Issue: "Channel is not currently live"

**Solution:** The channel is offline. Use a VOD URL instead:
```bash
python main.py --url "https://kick.com/video/VIDEO_ID" --generate-clips
```

### Issue: "No highlights detected"

**Solutions:**
1. Lower the minimum gap: `--min-gap 5`
2. Check if stream has audio/video
3. Try a different stream type: `--type both`

### Issue: Processing is slow

**Solutions:**
1. Increase `FRAME_SKIP` in `config.py`
2. Use larger `CHUNK_DURATION`
3. Process shorter streams first
4. Check internet speed

---

## 💡 Tips & Best Practices

### 1. Start with Analysis Only

```bash
# Don't use --generate-clips first
python main.py --url "https://kick.com/channelname"
```

This shows you the highlights without generating clips. If you like what you see, run again with `--generate-clips`.

### 2. Use the Right Highlight Type

- **Gaming streams**: `--type video` (visual action)
- **Talk shows/podcasts**: `--type audio` (reactions, excitement)
- **Mixed content**: `--type both` (default)

### 3. Adjust Clip Duration Based on Content

- **Fast-paced games**: `--clip-duration 20`
- **Story games**: `--clip-duration 45`
- **IRL streams**: `--clip-duration 30`

### 4. Test with Short Streams First

Start with a 30-minute VOD before processing a 6-hour stream.

### 5. Use yt-dlp for Best Results

```bash
pip install yt-dlp
```

This handles authentication automatically for Kick, Twitch, and YouTube.

---

## 📚 Example Workflows

### Workflow 1: Daily Highlight Compilation

```bash
# 1. Process today's stream
python main.py --url "https://kick.com/channelname" --generate-clips

# 2. Clips are saved to output_clips/
# 3. Use video editor to compile best clips
# 4. Upload to YouTube/TikTok
```

### Workflow 2: VOD Analysis

```bash
# 1. Find interesting VOD
# 2. Analyze without generating clips
python main.py --url "https://kick.com/video/VIDEO_ID"

# 3. Review timestamps in highlights.json
# 4. Generate clips if satisfied
python main.py --url "https://kick.com/video/VIDEO_ID" --generate-clips
```

### Workflow 3: Multi-Stream Comparison

```bash
# Process multiple streamers
python main.py --url "https://kick.com/streamer1" --generate-clips
python main.py --url "https://kick.com/streamer2" --generate-clips
python main.py --url "https://kick.com/streamer3" --generate-clips

# Compare highlights.json files to find best content
```

---

## 🎓 Learning Resources

- **README.md**: Overview and installation
- **ARCHITECTURE.md**: How the system works
- **TROUBLESHOOTING.md**: Fix common problems
- **KICK_STREAMS_GUIDE.md**: Kick-specific details
- **INTERFACE_GUIDE.md**: GUI usage

---

## 🆘 Need Help?

1. Run system test: `python test_system.py`
2. Check troubleshooting: `TROUBLESHOOTING.md`
3. Enable debug logging in `config.py`: `LOG_LEVEL = 'DEBUG'`

---

**Happy clipping! 🎬**
