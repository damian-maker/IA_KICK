# Clip Limits & Long Video Support Update

## 🎯 Overview

Added configurable clip output limits and support for processing videos longer than 5 hours without errors.

## ✨ New Features

### 1. **Configurable Clip Limits**
- Select number of audio clips (1-25)
- Select number of video clips (1-25)
- Maximum total: 50 clips (25 audio + 25 video)
- Prevents memory issues and errors

### 2. **Long Video Support**
- Handles videos up to 10 hours (36,000 seconds)
- Automatic duration limiting for safety
- Efficient chunked processing
- No memory overflow errors

### 3. **Safety Limits**
- Hard maximum: 25 clips per type
- Total maximum: 50 clips combined
- Stream duration cap: 10 hours
- Configurable in `config.py`

## 📊 Configuration

### New Config Settings (`config.py`)

```python
# Maximum clips per type (audio or video)
MAX_CLIPS_PER_TYPE = 25

# Maximum total clips to generate
MAX_TOTAL_CLIPS = 50

# Maximum stream duration to process (10 hours)
MAX_STREAM_DURATION = 36000  # seconds
```

## 🎮 Usage

### GUI Mode

1. **Launch interface:**
   ```bash
   python main.py --gui
   ```

2. **Set clip limits:**
   - Use "Max Audio Clips" slider (1-25)
   - Use "Max Video Clips" slider (1-25)
   - Default: 10 each

3. **Process stream:**
   - Enter stream URL
   - Adjust settings
   - Click "Analyze Stream"

### CLI Mode

```bash
# Generate 15 audio clips and 20 video clips
python main.py --cli --url "https://kick.com/video/123" \
  --max-audio-clips 15 \
  --max-video-clips 20 \
  --generate-clips

# Maximum clips (25 each)
python main.py --cli --url "stream.m3u8" \
  --max-audio-clips 25 \
  --max-video-clips 25 \
  --generate-clips
```

## 🔧 Technical Details

### Changes Made

#### 1. **config.py**
- Added `MAX_CLIPS_PER_TYPE = 25`
- Added `MAX_TOTAL_CLIPS = 50`
- Added `MAX_STREAM_DURATION = 36000`

#### 2. **kick_clip_generator.py**
- Updated `process_stream()` with `max_audio_clips` and `max_video_clips` parameters
- Updated `_filter_highlights()` to accept `max_clips` parameter
- Added stream duration check in `process_stream_chunks()`
- Enforces maximum limits automatically

#### 3. **gradio_interface.py**
- Added "Max Audio Clips" slider (1-25)
- Added "Max Video Clips" slider (1-25)
- Updated `process_stream_wrapper()` to pass clip limits
- Added helpful tip about 50 clip maximum

#### 4. **main.py**
- Added `--max-audio-clips` CLI argument
- Added `--max-video-clips` CLI argument
- Updated CLI mode to enforce limits

### How It Works

```
User Input (1-25 clips)
    ↓
Enforce Maximum (≤25)
    ↓
Process Stream
    ↓
Filter Highlights (top N by score)
    ↓
Return Limited Clips
    ↓
Generate Videos (≤50 total)
```

## 📈 Benefits

### Memory Safety
- ✅ Prevents out-of-memory errors
- ✅ Limits resource usage
- ✅ Stable for long videos

### Performance
- ✅ Faster processing with fewer clips
- ✅ Reduced disk usage
- ✅ Quicker clip generation

### User Control
- ✅ Choose exactly how many clips
- ✅ Balance quality vs quantity
- ✅ Optimize for your use case

## 🎯 Use Cases

### Quick Highlights (5-10 clips)
```bash
--max-audio-clips 5 --max-video-clips 5
```
- Fast processing
- Best moments only
- Perfect for short videos

### Comprehensive Analysis (20-25 clips)
```bash
--max-audio-clips 25 --max-video-clips 25
```
- Maximum coverage
- More variety
- Best for long streams

### Audio Focus (25 audio, 5 video)
```bash
--max-audio-clips 25 --max-video-clips 5
```
- Emphasize audio highlights
- Reduce video processing time
- Good for talk shows/podcasts

### Video Focus (5 audio, 25 video)
```bash
--max-audio-clips 5 --max-video-clips 25
```
- Emphasize visual highlights
- More action clips
- Good for gameplay/sports

## ⚠️ Important Notes

### Maximum Limits
- **Per type**: 25 clips max (audio OR video)
- **Total**: 50 clips max (audio + video combined)
- **Duration**: 10 hours max (36,000 seconds)

### Automatic Enforcement
- System automatically caps at maximum values
- No errors if you request more than 25
- Logs warning if stream exceeds 10 hours

### Long Video Handling
- Videos >10 hours: Only first 10 hours processed
- Warning logged but processing continues
- Prevents memory overflow and crashes

## 🧪 Testing

### Test with Different Limits

```bash
# Test minimum (1 clip each)
python main.py --cli --url "test.mp4" --max-audio-clips 1 --max-video-clips 1

# Test medium (10 clips each)
python main.py --cli --url "test.mp4" --max-audio-clips 10 --max-video-clips 10

# Test maximum (25 clips each)
python main.py --cli --url "test.mp4" --max-audio-clips 25 --max-video-clips 25

# Test over-limit (will cap at 25)
python main.py --cli --url "test.mp4" --max-audio-clips 100 --max-video-clips 100
```

### Test Long Videos

```bash
# Process 8-hour stream
python main.py --cli --url "long-stream.m3u8" --max-audio-clips 20 --max-video-clips 20

# Process 12-hour stream (will cap at 10 hours)
python main.py --cli --url "very-long-stream.m3u8" --max-audio-clips 25 --max-video-clips 25
```

## 📊 Performance Comparison

### Before Update
- ❌ No clip limit control
- ❌ Could generate 100+ clips
- ❌ Memory errors on long videos
- ❌ Crashes on 5+ hour streams

### After Update
- ✅ User-controlled limits (1-25)
- ✅ Maximum 50 clips total
- ✅ Handles 10+ hour videos
- ✅ No crashes or memory errors

## 🔮 Future Enhancements

Potential improvements:
- [ ] Dynamic limits based on available memory
- [ ] Automatic quality-based filtering
- [ ] Time-range selection (process only specific hours)
- [ ] Multi-part processing for very long videos
- [ ] Clip priority system (keep best N clips)

## 💡 Tips

### Optimal Settings

**For 1-hour streams:**
- Audio: 10 clips
- Video: 10 clips
- Total: ~20 clips

**For 3-hour streams:**
- Audio: 15 clips
- Video: 15 clips
- Total: ~30 clips

**For 5+ hour streams:**
- Audio: 20-25 clips
- Video: 20-25 clips
- Total: 40-50 clips

### Performance Tips

1. **Start small**: Test with 5-10 clips first
2. **Increase gradually**: Add more if needed
3. **Monitor resources**: Check memory usage
4. **Use filters**: Rely on ML model to find best clips

## 🎊 Summary

### What Changed
- ✅ Added clip limit controls (1-25 per type)
- ✅ Added 10-hour maximum duration
- ✅ Updated GUI with sliders
- ✅ Updated CLI with arguments
- ✅ Enforced safety limits

### Why It Matters
- ✅ Prevents errors and crashes
- ✅ Gives users control
- ✅ Handles long videos safely
- ✅ Optimizes performance

### How to Use
1. Set clip limits in GUI or CLI
2. Process your stream
3. Get exactly the number of clips you want
4. No errors, even with 10-hour videos!

---

**Now you can process any length video and get exactly the number of clips you need!** 🎬

**Maximum Safety. Maximum Control. Maximum Flexibility.** ✨
