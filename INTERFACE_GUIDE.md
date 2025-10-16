# 🖥️ Interface Guide

## Gradio Web Interface

### Starting the Interface

**Windows:**
```bash
run.bat
```

**Or manually:**
```bash
python main.py --gui
```

**Access at:** http://localhost:7860

---

## Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🎬 Kick Stream Clip Generator                              │
│  AI-Powered Highlight Detection with Continuous Learning    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔗 Stream URL: [_________________________________]          │
│                                                              │
│  ⏱️ Clip Duration: [====|====] 30s                          │
│  📏 Min Gap: [====|====] 10s                                │
│                                                              │
│  [🔍 Analyze Stream]                                        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  📊 Analysis Results                                         │
│  ✅ Analysis Complete!                                       │
│  🎵 Audio Highlights: 10                                     │
│  🎬 Video Highlights: 10                                     │
├─────────────────────────────────────────────────────────────┤
│  🎵 Audio Highlights        │  🎬 Video Highlights          │
│  ┌─────────────────────┐   │  ┌─────────────────────┐      │
│  │ Rank │ Time │ Score │   │  │ Rank │ Time │ Score │      │
│  │  1   │ 2:30 │ 8.5   │   │  │  1   │ 5:15 │ 9.2   │      │
│  │  2   │ 5:45 │ 7.8   │   │  │  2   │ 8:30 │ 8.7   │      │
│  └─────────────────────┘   │  └─────────────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  🎞️ Generate Clips                                          │
│  ○ Audio Only  ○ Video Only  ● Both                        │
│  [🎬 Generate Clips]                                        │
│                                                              │
│  📺 Clip Preview                                            │
│  [        Video Player        ]                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Usage

### Step 1: Enter Stream URL

**Input Field:** 🔗 Stream URL

**Accepted Formats:**
- ✅ Kick livestream: `https://kick.com/channelname`
- ✅ Kick VOD: `https://kick.com/video/12345`
- ✅ Direct M3U8: `https://example.com/stream.m3u8`
- ✅ Direct MP4: `https://example.com/video.mp4`

**Example:**
```
https://kick.com/xqc
```

### Step 2: Adjust Settings (Optional)

**⏱️ Clip Duration Slider**
- Range: 10-60 seconds
- Default: 30 seconds
- Purpose: Length of generated clips

**📏 Minimum Gap Slider**
- Range: 5-60 seconds
- Default: 10 seconds
- Purpose: Minimum time between highlights (prevents clustering)

**When to Adjust:**
- **Shorter clips (10-20s)**: For social media posts
- **Longer clips (45-60s)**: For full context
- **Larger gap (30-60s)**: For very long streams
- **Smaller gap (5-10s)**: For action-packed content

### Step 3: Analyze Stream

**Click:** 🔍 Analyze Stream

**What Happens:**
1. System validates URL
2. Resolves Kick URLs to playable streams
3. Downloads and processes chunks
4. Extracts audio and video features
5. Calculates highlight scores
6. Displays results

**Progress Indicator:**
```
Processing chunk 15 (450s / 28800s)
[████████░░░░░░░░░░░░░░░░░░░░] 15.6%
```

**Processing Time:**
- 1 hour stream: ~2-4 minutes
- 4 hour stream: ~8-15 minutes
- 8 hour stream: ~15-30 minutes

### Step 4: Review Results

**Analysis Results Box:**
```
✅ Analysis Complete!

📊 Results:
- 🎵 Audio Highlights: 10
- 🎬 Video Highlights: 10
- ⏱️ Total Highlights: 20

🎯 Top Scores:
- Best Audio: 8.52
- Best Video: 9.18

💾 Ready to generate clips!
```

**Audio Highlights Table:**
| Rank | Type  | Start Time | Duration | Score |
|------|-------|------------|----------|-------|
| 1    | Audio | 2:30       | 30s      | 8.52  |
| 2    | Audio | 5:45       | 30s      | 7.83  |
| 3    | Audio | 12:15      | 30s      | 7.21  |

**Video Highlights Table:**
| Rank | Type  | Start Time | Duration | Score |
|------|-------|------------|----------|-------|
| 1    | Video | 5:15       | 30s      | 9.18  |
| 2    | Video | 8:30       | 30s      | 8.67  |
| 3    | Video | 15:45      | 30s      | 8.12  |

**Understanding Scores:**
- **8.0+**: Excellent highlight
- **6.0-8.0**: Good highlight
- **4.0-6.0**: Moderate highlight
- **< 4.0**: Weak highlight

### Step 5: Generate Clips

**Select Highlight Type:**
- ○ **Audio Only**: Generate clips from audio highlights only
- ○ **Video Only**: Generate clips from video highlights only
- ● **Both**: Generate all clips (default)

**Click:** 🎬 Generate Clips

**What Happens:**
1. Extracts selected highlights from stream
2. Saves clips to `output_clips/` directory
3. Generates metadata JSON file
4. Shows first clip in preview

**Output:**
```
✅ Clips Generated Successfully!

📁 Output:
- Generated 20 clips
- Location: output_clips/
- Metadata: highlights_20241012_185230.json

🎬 Clips:
- audio_highlight_1_audio.mp4
- audio_highlight_2_audio.mp4
- video_highlight_1_video.mp4
- video_highlight_2_video.mp4
...
```

### Step 6: Preview and Use

**📺 Clip Preview:**
- First generated clip plays automatically
- Use video controls to play/pause
- Download button available

**Access All Clips:**
```
output_clips/
├── audio_highlight_1_audio.mp4
├── audio_highlight_2_audio.mp4
├── video_highlight_1_video.mp4
└── highlights_20241012_185230.json
```

---

## Advanced Features

### Progress Tracking

During analysis, you'll see:
```
🔍 Processing chunk 25 (750s / 28800s)
```

**Information:**
- Current chunk number
- Current time position
- Total stream duration
- Percentage complete

### Error Messages

**❌ Please provide a stream URL**
- Solution: Enter a valid URL

**❌ Error: 403 Forbidden**
- System automatically retries
- If persists, check URL validity

**⚠️ Already processing a stream**
- Wait for current processing to complete
- Or refresh page

### Model Statistics

**Click:** 📈 Model Statistics (accordion)

Shows:
- Training samples collected
- Model performance metrics
- Prediction accuracy
- Feature importance

---

## Tips for Best Results

### 1. Stream Quality
- ✅ High-quality streams = better detection
- ✅ Clear audio = better audio highlights
- ✅ Action-packed content = better video highlights

### 2. Settings Optimization

**For Gaming Streams:**
```
Clip Duration: 30-45s
Min Gap: 10-15s
```

**For Talk Shows:**
```
Clip Duration: 20-30s
Min Gap: 15-30s
```

**For Music Streams:**
```
Clip Duration: 45-60s
Min Gap: 20-30s
```

### 3. Processing Multiple Streams

**First Stream:**
- Uses heuristic scoring only
- Establishes baseline

**Subsequent Streams:**
- ML model kicks in
- Predictions improve
- Better highlight detection

**Recommendation:** Process 3-5 streams for optimal ML performance

### 4. Reviewing Results

**High Scores (8.0+):**
- Definitely worth reviewing
- Likely exciting moments

**Medium Scores (6.0-8.0):**
- Good candidates
- May need manual review

**Low Scores (< 6.0):**
- Less exciting
- Consider adjusting thresholds

---

## Keyboard Shortcuts

While interface is focused:
- **Enter**: Submit form
- **Tab**: Navigate fields
- **Space**: Toggle buttons
- **Esc**: Close modals

---

## Mobile/Tablet Usage

The interface is responsive and works on mobile devices:

**Access:**
```bash
python main.py --gui --server-name 0.0.0.0
```

Then access from mobile: `http://your-computer-ip:7860`

**Limitations:**
- Smaller screen = less visible
- Processing still happens on computer
- Preview may be limited

---

## Sharing Interface

**Create Public Link:**
```bash
python main.py --gui --share
```

**Output:**
```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://abc123.gradio.live
```

**Share the public URL** with others (expires after 72 hours)

**Security Note:** Anyone with the link can use your system

---

## Customizing Interface

### Change Port

```bash
python main.py --gui --port 8080
```

Access at: http://localhost:8080

### Change Theme

Edit `gradio_interface.py`:
```python
theme=gr.themes.Soft(
    primary_hue="green",  # Change color
    secondary_hue="blue",
)
```

Available themes:
- `gr.themes.Soft()`
- `gr.themes.Base()`
- `gr.themes.Glass()`
- `gr.themes.Monochrome()`

---

## CLI Alternative

If you prefer command-line:

```bash
# Analyze only
python main.py --url "https://kick.com/channel"

# Analyze and generate clips
python main.py --url "https://kick.com/channel" --generate-clips

# Custom settings
python main.py --url "stream.m3u8" --clip-duration 45 --min-gap 15 --generate-clips --type both
```

See `main.py --help` for all options.

---

## Interface States

### Initial State
- All fields empty
- Generate button disabled
- No results shown

### Processing State
- Progress bar active
- Analyze button disabled
- "Processing..." message

### Results State
- Tables populated
- Generate button enabled
- Summary shown

### Error State
- Error message displayed
- Fields remain editable
- Can retry

---

## Troubleshooting Interface

### Interface Won't Load

**Check:**
1. Port not in use: `netstat -ano | findstr :7860`
2. Firewall allows Python
3. Gradio installed: `pip show gradio`

### Slow Response

**Causes:**
- Large stream processing
- Slow internet
- Limited CPU

**Solutions:**
- Wait for completion
- Use smaller streams
- Adjust settings

### Preview Not Working

**Solutions:**
1. Check browser supports video format
2. Try different browser
3. Download clip manually from `output_clips/`

---

## Best Practices

1. **Start Small**: Test with 1-2 hour streams first
2. **Review Results**: Check a few clips before generating all
3. **Adjust Settings**: Fine-tune based on content type
4. **Monitor Progress**: Watch for errors during processing
5. **Save Metadata**: Keep JSON files for reference

---

**Ready to use the interface!** 🚀

Launch with: `python main.py --gui` or `run.bat`
