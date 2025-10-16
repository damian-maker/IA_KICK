# 🎬 Kick Stream Clip Generator

An advanced AI-powered tool for automatically detecting and generating highlight clips from Kick streaming platform videos using machine learning. The system continuously improves its performance over time through adaptive learning.

## ✨ Features

### 🎯 Core Capabilities
- **Live & VOD Support**: Process both **live streams** and **past streams (VODs)** from Kick.com
- **Chunked Processing**: Processes streams in segments without downloading full videos (perfect for 8-9 hour streams)
- **Dual Analysis**: 
  - 🎵 **Audio Analysis**: Detects exciting moments through volume, spectral features, tempo, and voice characteristics
  - 🎬 **Video Analysis**: Identifies action through motion detection, visual complexity, and scene changes
- **Machine Learning**: Continuously improving ML models that learn from each processed stream
- **Robust Error Handling**: Gracefully handles 403 errors with exponential backoff and user agent rotation
- **Beautiful Gradio Interface**: Modern, intuitive web UI for easy operation
- **yt-dlp Integration**: Automatic authentication for Kick, Twitch, and YouTube streams

### ⭐ NEW: Clip Management & Rating System
- **📊 Clip Database**: All clips tracked in SQLite database with metadata
- **⭐ Rating System**: Rate clips 1-5 stars to teach the AI your preferences
- **🎓 Continuous Learning**: Model automatically retrains based on your ratings
- **📂 Clip Gallery**: Browse, view, and download all generated clips
- **📈 Statistics Dashboard**: Track ratings, model performance, and improvement
- **🔄 Auto-Training**: Model improves every 5 ratings (configurable)
- **💾 Persistent Storage**: Ratings and training data saved between sessions

### 🎛️ NEW: Configurable Clip Limits & Long Video Support
- **🎚️ Adjustable Output**: Select 1-25 clips per type (audio/video)
- **🛡️ Safety Limits**: Maximum 50 total clips to prevent errors
- **⏰ Long Video Support**: Handles streams up to 10 hours without crashes
- **💪 Memory Safe**: Prevents out-of-memory errors on long videos
- **🎮 User Control**: Choose exactly how many clips to generate

### 🚀 Performance Optimized
- Processes only necessary chunks, not full videos
- Frame skipping for faster video analysis
- Parallel processing capabilities
- Minimal memory footprint
- Optimized for long-duration streams (8-9 hours)

### 🧠 Machine Learning
- **Gradient Boosting Models** for both audio and video analysis
- **Continuous Learning**: Models improve with each stream processed
- **Feature Engineering**: 20+ audio and video features extracted
- **Adaptive Scoring**: Combines heuristic and ML-based scoring

## 📋 Requirements

- Python 3.8+
- FFmpeg installed on system
- 4GB+ RAM recommended
- Internet connection for stream access

## 🔧 Installation

1. **Clone or download this repository**

2. **Install FFmpeg** (if not already installed):
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Linux**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install yt-dlp** (recommended for Kick streams):
```bash
pip install yt-dlp
```

## 🎮 Usage

### Quick Start - GUI Mode (Recommended)

1. **Launch the interface**:
```bash
python main.py --gui
# Or use: run.bat (Windows)
```

2. **Open your browser** to `http://localhost:7860`

3. **Tab 1 - Generate Clips**:
   - Enter a stream URL (Kick.com or direct video)
   - Click "Analyze Stream"
   - Review detected highlights
   - Click "Generate Clips"

4. **Tab 2 - Rate Clips** ⭐ NEW:
   - Click "Load Clips for Rating"
   - Watch and rate clips 1-5 stars
   - Model automatically improves with your ratings!

5. **Tab 3 - Browse & Download** 📂 NEW:
   - View all clips in gallery
   - Download your favorites
   - See ratings and scores

### Quick Start - CLI Mode

**Process a live stream:**
```bash
python main.py --url "https://kick.com/channelname" --generate-clips
```

**Process a past stream (VOD):**
```bash
python main.py --url "https://kick.com/video/VIDEO_ID" --generate-clips
```

**Custom settings:**
```bash
python main.py --url "stream_url" --clip-duration 45 --min-gap 15 --generate-clips
```

**Control clip output (NEW):**
```bash
# Generate 15 audio clips and 20 video clips
python main.py --url "stream_url" --max-audio-clips 15 --max-video-clips 20 --generate-clips

# Maximum clips (25 each, 50 total)
python main.py --url "stream_url" --max-audio-clips 25 --max-video-clips 25 --generate-clips
```

### Command Line Usage

```python
from kick_clip_generator import KickClipGenerator

# Initialize generator
generator = KickClipGenerator(clip_duration=30, min_gap=10)

# Process stream
stream_url = "https://your-stream-url.m3u8"
audio_highlights, video_highlights = generator.process_stream(stream_url)

# Generate clips
all_highlights = audio_highlights + video_highlights
clips = generator.generate_clips(stream_url, all_highlights)

# Export metadata
generator.export_highlights_json(audio_highlights, video_highlights)
```

## 📊 How It Works

### 1. Stream Processing
- Stream is divided into 30-second chunks with 5-second overlap
- Each chunk is downloaded temporarily and processed
- Chunks are deleted after processing to save space

### 2. Feature Extraction

**Audio Features (13+ features)**:
- RMS energy (volume)
- Spectral centroid (brightness)
- Zero-crossing rate (voice activity)
- Tempo and beat strength
- MFCCs (voice characteristics)
- High-frequency energy (excitement)

**Video Features (8+ features)**:
- Motion detection (frame differences)
- Edge density (action indicator)
- Color variance (visual complexity)
- Brightness analysis

### 3. Highlight Detection
- Heuristic scoring based on feature analysis
- ML model predictions (when trained)
- Combined scoring (60% heuristic, 40% ML)
- Top 10 highlights selected per type

### 4. Continuous Learning
- Features and scores stored as training data
- Models retrain after each stream
- Performance improves over time
- Models saved automatically

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Processing settings
CHUNK_DURATION = 30  # seconds per chunk
TOP_N_HIGHLIGHTS = 10  # number of highlights to return

# ML settings
N_ESTIMATORS = 100  # gradient boosting trees
LEARNING_RATE = 0.1  # model learning rate

# Network settings
MAX_RETRIES = 5  # retry attempts for 403 errors
BACKOFF_FACTOR = 2  # exponential backoff multiplier
```

## 🛡️ Error Handling

### 403 Errors
- Automatic retry with exponential backoff
- User agent rotation
- Configurable retry attempts
- Graceful degradation

### Network Issues
- Timeout handling
- Connection retry logic
- Partial processing support

### Processing Errors
- Individual chunk failures don't stop processing
- Comprehensive logging
- Error recovery mechanisms

## 📁 Output Structure

```
IA_KICK/
├── output_clips/          # Generated video clips
│   ├── audio_highlight_1_audio.mp4
│   ├── video_highlight_1_video.mp4
│   └── highlights_20241012_185230.json
├── models/                # ML models (auto-created)
│   └── highlight_model.pkl
├── temp_chunks/           # Temporary processing files
└── logs/                  # Processing logs
```

## 🎯 Use Cases

1. **Content Creators**: Automatically generate highlight reels from long streams
2. **Esports**: Extract exciting gameplay moments
3. **VOD Processing**: Create compilations from archived streams
4. **Social Media**: Generate shareable clips for promotion
5. **Analysis**: Study stream engagement patterns

## 🔍 Advanced Features

### Custom Feature Weights
Modify scoring in `kick_clip_generator.py`:

```python
# Audio scoring
score += features.get('rms_mean', 0) * 2.0  # Increase weight
score += features.get('zcr_mean', 0) * 1.0

# Video scoring
score += features.get('motion_mean', 0) * 2.0
score += features.get('edge_density_mean', 0) * 100.0
```

### ML Model Customization
Change model type in `MLHighlightModel`:

```python
from sklearn.ensemble import RandomForestRegressor

self.audio_model = RandomForestRegressor(n_estimators=200)
```

### Batch Processing
Process multiple streams:

```python
stream_urls = ['url1', 'url2', 'url3']
for url in stream_urls:
    audio_h, video_h = generator.process_stream(url)
    generator.generate_clips(url, audio_h + video_h)
```

## 📈 Performance Tips

1. **Adjust chunk duration**: Smaller chunks = faster processing, but more overhead
2. **Increase frame skip**: Process every 10th frame instead of 5th for speed
3. **Reduce overlap**: Less overlap = faster, but might miss highlights
4. **Use GPU**: Enable GPU acceleration in config for video processing
5. **Parallel processing**: Increase MAX_WORKERS for multi-core systems

## 🐛 Troubleshooting

### Issue: 403 Errors Persist
- Increase MAX_RETRIES in config
- Add more user agents to rotation
- Check if stream requires authentication

### Issue: Slow Processing
- Reduce CHUNK_DURATION
- Increase FRAME_SKIP
- Check internet connection speed

### Issue: No Highlights Detected
- Lower MIN_AUDIO_SCORE and MIN_VIDEO_SCORE
- Adjust feature weights
- Check stream quality

### Issue: Out of Memory
- Reduce CHUNK_DURATION
- Increase FRAME_SKIP
- Close other applications

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional feature extraction methods
- More ML model types
- Better error handling
- Performance optimizations
- UI enhancements

## 📝 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

Built with:
- **Gradio** - Web interface
- **FFmpeg** - Video processing
- **librosa** - Audio analysis
- **OpenCV** - Video analysis
- **scikit-learn** - Machine learning

## ⭐ Rating System & Model Improvement

### How It Works
1. **Generate clips** from your streams
2. **Rate clips** 1-5 stars based on quality
3. **Model learns** from your ratings automatically
4. **Better highlights** generated in future streams

### Getting Started with Ratings
```bash
# 1. Generate some clips first
python main.py --gui

# 2. Go to "Rate Clips" tab
# 3. Rate at least 10 clips
# 4. Model trains automatically
# 5. Generate new clips and see improvement!
```

### Documentation
- **Quick Start**: See `QUICK_START_RATING.md`
- **Full Guide**: See `CLIP_MANAGEMENT_GUIDE.md`
- **Feature Summary**: See `FEATURE_SUMMARY.md`

### Key Benefits
✅ **Personalized** - AI learns YOUR preferences  
✅ **Automatic** - Model trains every 5 ratings  
✅ **Persistent** - Ratings saved in database  
✅ **Visual** - Track progress with statistics  

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in console output
3. Verify FFmpeg installation
4. Check stream URL validity
5. Read `CLIP_MANAGEMENT_GUIDE.md` for rating system help

## 🧪 Testing

Run the test suite to verify everything works:
```bash
python test_clip_management.py
```

All tests should pass ✅

---

**Made with ❤️ for the streaming community**

**New in this version**: Clip management, rating system, and continuous learning! 🎉
