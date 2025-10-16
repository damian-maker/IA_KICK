# 🏗️ System Architecture

## Overview

The Kick Clip Generator is a modular system designed for efficient processing of long-duration streams with machine learning-based highlight detection.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                          │
├─────────────────────────────────────────────────────────────┤
│  Gradio Web UI              CLI Interface                    │
│  (gradio_interface.py)      (main.py)                       │
└─────────────────┬───────────────────────┬───────────────────┘
                  │                       │
                  ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  CORE ORCHESTRATOR                           │
├─────────────────────────────────────────────────────────────┤
│              KickClipGenerator                               │
│         (kick_clip_generator.py)                            │
│  - Coordinates all components                                │
│  - Manages processing pipeline                               │
│  - Handles output generation                                 │
└──┬────────────┬────────────┬────────────┬────────────┬──────┘
   │            │            │            │            │
   ▼            ▼            ▼            ▼            ▼
┌──────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌────────┐
│Stream│  │  Audio   │  │  Video   │  │   ML   │  │  Kick  │
│Proc. │  │ Analyzer │  │ Analyzer │  │  Model │  │  API   │
└──────┘  └──────────┘  └──────────┘  └────────┘  └────────┘
```

## Core Components

### 1. Stream Processor (`StreamProcessor`)
**Purpose:** Handles video stream chunking and downloading

**Key Features:**
- Chunks streams into manageable segments (default: 30s)
- Uses FFmpeg for efficient extraction
- Implements overlap to avoid missing highlights
- Temporary file management

**Flow:**
```
Stream URL → Get Info → Download Chunks → Process → Cleanup
```

### 2. Audio Analyzer (`AudioAnalyzer`)
**Purpose:** Extracts and analyzes audio features

**Features Extracted (13+):**
- RMS Energy (volume)
- Spectral Centroid (brightness)
- Zero-Crossing Rate (voice activity)
- Tempo & Beat Strength
- MFCCs (voice characteristics)
- High-Frequency Energy (excitement)
- Loudness Variance

**Scoring Algorithm:**
```python
score = (rms_mean * 2.0) + 
        (rms_std * 1.5) + 
        (zcr_mean * 1.0) + 
        (spectral_centroid / 1000) + 
        (loudness_variance * 0.5) + 
        (high_freq_energy / 1e9)
```

### 3. Video Analyzer (`VideoAnalyzer`)
**Purpose:** Extracts and analyzes video features

**Features Extracted (8+):**
- Motion Detection (frame differences)
- Edge Density (action indicator)
- Color Variance (visual complexity)
- Brightness Analysis

**Optimization:**
- Frame skipping (every 5th frame)
- Grayscale conversion for speed
- Efficient OpenCV operations

**Scoring Algorithm:**
```python
score = (motion_mean * 2.0) + 
        (motion_std * 1.5) + 
        (edge_density_mean * 100.0) + 
        (edge_density_std * 50.0) + 
        (color_variance_mean / 1000.0)
```

### 4. ML Highlight Model (`MLHighlightModel`)
**Purpose:** Machine learning for continuous improvement

**Architecture:**
- Gradient Boosting Regressor (100 trees)
- Separate models for audio and video
- StandardScaler for feature normalization
- Persistent storage (pickle)

**Learning Process:**
```
1. Collect features + heuristic scores
2. Store as training data
3. Retrain when sufficient samples (10+)
4. Combine ML predictions with heuristics
   - 60% heuristic score
   - 40% ML score
5. Save model for future use
```

### 5. Kick API (`KickAPI`)
**Purpose:** Interface with Kick.com platform

**Capabilities:**
- URL parsing and channel extraction
- Livestream URL resolution
- VOD URL retrieval
- Stream metadata extraction

### 6. Retry Session (`RetrySession`)
**Purpose:** Robust HTTP handling with 403 error resistance

**Features:**
- Exponential backoff (2^attempt seconds)
- User agent rotation
- Configurable retry attempts (default: 5)
- Timeout handling (default: 30s)

**Retry Strategy:**
```
Attempt 1: Wait 1s  (2^0)
Attempt 2: Wait 2s  (2^1)
Attempt 3: Wait 4s  (2^2)
Attempt 4: Wait 8s  (2^3)
Attempt 5: Wait 16s (2^4)
```

## Processing Pipeline

### Full Processing Flow

```
1. INPUT
   ├─ Stream URL provided
   └─ Resolve if Kick URL
   
2. STREAM ANALYSIS
   ├─ Get stream metadata
   ├─ Calculate total duration
   └─ Determine chunk count
   
3. CHUNK PROCESSING (Loop)
   ├─ Download chunk (30s)
   ├─ Extract audio features
   ├─ Extract video features
   ├─ Calculate heuristic scores
   ├─ Get ML predictions
   ├─ Combine scores
   ├─ Store as highlight candidate
   └─ Delete chunk
   
4. HIGHLIGHT SELECTION
   ├─ Sort by score
   ├─ Remove overlaps (min gap)
   ├─ Select top N (default: 10)
   └─ Separate audio/video
   
5. ML TRAINING
   ├─ Add samples to training data
   ├─ Retrain models
   └─ Save updated models
   
6. CLIP GENERATION (Optional)
   ├─ Extract clips from stream
   ├─ Save to output directory
   └─ Export metadata JSON
   
7. OUTPUT
   ├─ Highlight lists
   ├─ Video clips
   └─ Metadata JSON
```

## Data Flow

### Feature Extraction Pipeline

```
Video Chunk (30s)
    │
    ├─────────────────┬─────────────────┐
    ▼                 ▼                 ▼
Audio Track      Video Frames      Metadata
    │                 │                 │
    ▼                 ▼                 ▼
librosa          OpenCV            FFmpeg
    │                 │                 │
    ▼                 ▼                 ▼
13+ Features     8+ Features      Duration, FPS
    │                 │                 │
    └─────────────────┴─────────────────┘
                      │
                      ▼
              Feature Dictionary
                      │
                      ├─────────────┬─────────────┐
                      ▼             ▼             ▼
                  Heuristic      ML Model     Combined
                   Scoring      Prediction     Score
                      │             │             │
                      └─────────────┴─────────────┘
                                    │
                                    ▼
                            Highlight Object
```

## Performance Optimizations

### Memory Management
- **Chunked Processing:** Only one chunk in memory at a time
- **Temporary Files:** Deleted immediately after processing
- **Frame Skipping:** Process every 5th frame (80% reduction)
- **Grayscale Conversion:** Reduces data by 66%

### Processing Speed
- **Parallel Potential:** Independent chunks can be processed in parallel
- **FFmpeg Direct Extraction:** No full download required
- **Optimized Libraries:** NumPy, OpenCV, librosa
- **Feature Caching:** ML model loaded once

### Network Resilience
- **Exponential Backoff:** Prevents hammering servers
- **User Agent Rotation:** Avoids detection
- **Partial Processing:** Continues despite chunk failures
- **Timeout Handling:** Prevents hanging

## Configuration System

### Hierarchy
```
config.py (defaults)
    │
    ├─ Runtime overrides (CLI args)
    │
    └─ GUI overrides (Gradio inputs)
```

### Key Settings
- `CHUNK_DURATION`: 30s (balance between memory and accuracy)
- `FRAME_SKIP`: 5 (balance between speed and detail)
- `TOP_N_HIGHLIGHTS`: 10 (user requirement)
- `MIN_GAP_BETWEEN_HIGHLIGHTS`: 10s (avoid clustering)

## Error Handling Strategy

### Levels of Resilience

1. **Request Level**
   - Retry with backoff
   - User agent rotation
   - Timeout handling

2. **Chunk Level**
   - Skip failed chunks
   - Continue processing
   - Log errors

3. **Stream Level**
   - Partial results
   - Graceful degradation
   - User notification

4. **System Level**
   - Comprehensive logging
   - State preservation
   - Recovery mechanisms

## File Structure

```
IA_KICK/
├── kick_clip_generator.py    # Core processing engine
├── gradio_interface.py        # Web UI
├── kick_api.py                # Kick.com integration
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── QUICK_START.md            # Quick guide
├── ARCHITECTURE.md           # This file
├── example_usage.py          # Examples
├── test_system.py            # System tests
├── run.bat                   # Windows launcher
├── .gitignore                # Git ignore rules
│
├── temp_chunks/              # Temporary processing files
├── output_clips/             # Generated clips
├── models/                   # ML models
│   └── highlight_model.pkl   # Trained model
└── logs/                     # Log files
```

## Extension Points

### Adding New Features

1. **Audio Features:**
   - Add extraction in `AudioAnalyzer.extract_audio_features()`
   - Update scoring in `detect_audio_highlights()`

2. **Video Features:**
   - Add extraction in `VideoAnalyzer.extract_video_features()`
   - Update scoring in `detect_video_highlights()`

3. **ML Models:**
   - Replace in `MLHighlightModel.__init__()`
   - Maintain same interface

4. **Stream Sources:**
   - Add resolver in `KickAPI`
   - Follow same URL pattern

## Performance Metrics

### Expected Performance (8-hour stream)

- **Processing Time:** 15-30 minutes
- **Memory Usage:** < 2GB peak
- **Disk Usage:** < 500MB temporary
- **Network:** ~1-2GB downloaded (chunks only)

### Comparison to Full Download

- **Full Download:** 8-10GB, 30-60 minutes
- **Chunked Processing:** 1-2GB, 15-30 minutes
- **Savings:** 80% bandwidth, 50% time

## Security Considerations

- No hardcoded credentials
- User agent rotation for privacy
- Temporary file cleanup
- No sensitive data storage
- HTTPS for all requests

## Future Enhancements

1. **GPU Acceleration:** CUDA support for video processing
2. **Distributed Processing:** Multi-machine support
3. **Real-time Processing:** Live stream analysis
4. **Advanced ML:** Deep learning models (CNN, RNN)
5. **Cloud Integration:** S3, GCS storage
6. **API Server:** REST API for integration

---

**Design Philosophy:** Modular, efficient, resilient, and continuously improving.
