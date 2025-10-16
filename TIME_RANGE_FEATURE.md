# Time Range Feature Documentation

## Overview
Added the ability to specify start and end times (in minutes) to analyze only specific portions of videos, without causing any errors.

## Features Added

### 1. CLI Interface
Use `--start-minute` and `--end-minute` arguments:

```bash
# Analyze minutes 10-30 of a video
python main.py --url "video.mp4" --start-minute 10 --end-minute 30 --generate-clips

# Analyze from minute 5 to the end
python main.py --url "video.mp4" --start-minute 5 --generate-clips

# Analyze from beginning to minute 20
python main.py --url "video.mp4" --end-minute 20 --generate-clips
```

### 2. GUI Interface
Two new input fields in the web interface:
- **Start Minute**: Start analyzing from this minute (0 = from beginning)
- **End Minute**: Stop analyzing at this minute (0 = until end)

## Implementation Details

### Error Handling
The implementation includes robust validation:

1. **Negative start time**: Automatically corrected to 0
2. **End time exceeds duration**: Automatically capped to video duration
3. **Invalid range (start >= end)**: Logs error and skips processing
4. **Respects MAX_STREAM_DURATION**: Still enforces the 10-hour limit from config

### How It Works

1. **Time conversion**: Minutes are converted to seconds internally
2. **Chunk processing**: Only processes chunks within the specified range
3. **Progress tracking**: Progress bar shows correct percentage for the selected range
4. **Highlight timestamps**: All timestamps are absolute (relative to original video start)

### Example Use Cases

- **Long VODs**: Analyze only the interesting part (e.g., final 30 minutes of a tournament)
- **Testing**: Quick testing on a small segment before processing the full video
- **Specific events**: Target a known time range where action occurred
- **Memory management**: Process very long videos in segments

## Technical Changes

### Modified Files:
1. `kick_clip_generator.py`:
   - Updated `StreamProcessor.process_stream_chunks()` to accept `start_minute` and `end_minute`
   - Updated `KickClipGenerator.process_stream()` to pass through time parameters
   - Added validation and logging for time ranges

2. `main.py`:
   - Added `--start-minute` and `--end-minute` CLI arguments
   - Added logging for time range
   - Updated example usage in help text

3. `gradio_interface.py`:
   - Added start/end minute number inputs to the UI
   - Updated `process_stream_wrapper()` to handle time parameters
   - Converts 0 values to None for "use default" behavior

## Validation Examples

```python
# Valid ranges
start=0, end=30     # First 30 minutes
start=10, end=None  # From minute 10 to end
start=None, end=20  # From beginning to minute 20

# Auto-corrected ranges
start=-5, end=30    # Corrected to start=0
start=10, end=999   # Capped to video duration

# Invalid (will error)
start=30, end=10    # Start >= End (logged and skipped)
```

## Performance Benefits

- **Faster processing**: Only analyze the portion you need
- **Lower memory usage**: Fewer chunks to process
- **Targeted results**: Get highlights from specific segments
- **Better for testing**: Quick iterations on small segments

## Notes

- Time values are in **minutes** (can use decimals, e.g., 2.5 = 2 minutes 30 seconds)
- All highlight timestamps remain absolute (relative to original video start)
- Generated clips use the original video timestamps
- Works with all video sources (VODs, streams, local files)
