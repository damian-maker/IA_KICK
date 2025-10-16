# Clip Management & Rating System Guide

## Overview

The Kick Clip Generator now includes a comprehensive clip management system that allows you to:
- **View** all generated clips in a gallery
- **Download** clips individually
- **Rate** clips to improve the ML model over time

## Features

### 1. Clip Database
All generated clips are automatically registered in a SQLite database (`clips.db`) that tracks:
- Clip metadata (filename, duration, timestamps)
- Feature vectors used for detection
- User ratings (1-5 stars)
- Source stream information

### 2. Rating System
Rate clips from 1-5 stars to provide feedback to the ML model:
- ⭐ 1 - Poor highlight
- ⭐⭐ 2 - Below average
- ⭐⭐⭐ 3 - Average
- ⭐⭐⭐⭐ 4 - Good highlight
- ⭐⭐⭐⭐⭐ 5 - Excellent highlight

### 3. Continuous Learning
The ML model automatically improves based on your ratings:
- **Auto-training**: Model retrains every 5 new ratings
- **Manual training**: Train on-demand via the interface
- **Minimum samples**: Requires 10 rated clips to begin training

## Using the Interface

### Tab 1: Generate Clips
1. Enter a stream URL (Kick.com or direct video URL)
2. Adjust clip duration and minimum gap settings
3. Click "Analyze Stream" to detect highlights
4. Review detected audio and video highlights
5. Click "Generate Clips" to create video files
6. Clips are automatically saved and registered in the database

### Tab 2: View & Rate Clips
1. Click "Load Clips for Rating" to see unrated clips
2. Select a clip from the dropdown
3. Watch the clip preview
4. Choose a rating (1-5 stars)
5. Click "Submit Rating"
6. The model will automatically retrain when enough ratings are collected

**Statistics & Training:**
- View database statistics (total clips, ratings, distribution)
- Check ML model training status
- Manually trigger model training with "Train Model Now"

### Tab 3: Browse & Download
1. Click "Refresh Gallery" to view all clips
2. Browse clips with their ratings and scores
3. Select a clip from the dropdown
4. Click "Download" to save it locally

## Database Schema

The `clips.db` SQLite database contains:

```sql
CREATE TABLE clips (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    duration REAL NOT NULL,
    score REAL NOT NULL,
    clip_type TEXT NOT NULL,  -- 'audio' or 'video'
    features TEXT NOT NULL,   -- JSON string
    rating INTEGER,           -- 1-5 or NULL
    created_at TEXT NOT NULL,
    rated_at TEXT,
    source_url TEXT
);
```

## ML Model Training

### How It Works
1. **Feature Extraction**: Each clip has audio/video features extracted during generation
2. **User Ratings**: Your ratings (1-5 stars) serve as ground truth labels
3. **Normalization**: Ratings are normalized to 0-1 scale for training
4. **Training**: Gradient Boosting models learn to predict good highlights
5. **Improvement**: Future highlight detection uses learned patterns

### Training Process
- **Automatic**: Triggers every 5 new ratings
- **Manual**: Use "Train Model Now" button
- **Requirements**: Minimum 10 rated clips
- **Models**: Separate models for audio and video highlights

### Model Files
- Location: `models/highlight_model.pkl`
- Contains: Trained models, scalers, and training data
- Persistence: Automatically saved after training

## API Usage

### Programmatic Access

```python
from clip_manager import ClipManager
from model_trainer import RatingBasedTrainer

# Initialize
manager = ClipManager()

# Get statistics
stats = manager.get_statistics()
print(f"Total clips: {stats['total_clips']}")
print(f"Average rating: {stats['average_rating']}")

# Rate a clip
manager.rate_clip(clip_id=1, rating=5)

# Train model
trainer = RatingBasedTrainer(manager)
success = trainer.train_from_ratings(min_samples=10)
```

### Register Clips Manually

```python
clip_id = manager.register_clip(
    filepath="/path/to/clip.mp4",
    start_time=120.5,
    end_time=150.5,
    score=0.85,
    clip_type="audio",
    features={"rms_mean": 0.5, "tempo": 120},
    source_url="https://example.com/stream"
)
```

## Best Practices

### Rating Guidelines
1. **Be consistent**: Use the same criteria for all clips
2. **Consider context**: What makes a good highlight for your use case?
3. **Rate honestly**: Poor ratings help the model learn what to avoid
4. **Rate variety**: Rate both good and bad clips for balanced training

### Model Improvement
1. **Start with 10+ ratings**: Minimum for initial training
2. **Rate regularly**: Model improves with more data
3. **Review statistics**: Check rating distribution for balance
4. **Retrain periodically**: Use manual training button after major rating sessions

### Database Management
1. **Backup regularly**: Copy `clips.db` to preserve ratings
2. **Clean up**: Use `manager.cleanup_missing_files()` to remove orphaned entries
3. **Export data**: Use statistics to track improvement over time

## Troubleshooting

### No Clips Available for Rating
- Generate clips first in the "Generate Clips" tab
- Check that clips were successfully created in `output_clips/`

### Model Not Training
- Ensure you have at least 10 rated clips
- Check logs for training errors
- Verify `models/` directory exists and is writable

### Database Errors
- Check that `clips.db` is not locked by another process
- Ensure write permissions in the project directory
- Delete `clips.db` to reset (will lose all ratings)

### Gallery Not Showing Clips
- Click "Refresh Gallery" button
- Verify clips exist in `output_clips/` directory
- Check file paths in database match actual files

## Advanced Features

### Custom Training Parameters

```python
# Adjust minimum samples required
trainer.train_from_ratings(min_samples=20)

# Get training progress
progress = trainer.get_training_progress()
print(f"Ready for training: {progress['ready_for_training']}")
```

### Export Training Data

```python
# Get features and ratings for external analysis
features, ratings = manager.get_training_data()

# Export to CSV or other formats
import pandas as pd
df = pd.DataFrame(features)
df['rating'] = ratings
df.to_csv('training_data.csv', index=False)
```

### Batch Rating

```python
# Rate multiple clips at once
clips = manager.get_clips_for_review(limit=50)
for clip in clips:
    # Your rating logic here
    rating = determine_rating(clip)
    manager.rate_clip(clip.id, rating)
```

## Performance Tips

1. **Database size**: SQLite handles thousands of clips efficiently
2. **Gallery loading**: Limit gallery to 50 most recent clips
3. **Training frequency**: Auto-training every 5 ratings balances performance and improvement
4. **Feature storage**: JSON format allows flexible feature sets

## Future Enhancements

Potential improvements to the system:
- Multi-user rating support
- Rating confidence scores
- Clip tagging and categorization
- Export/import rating datasets
- A/B testing of model versions
- Real-time model performance metrics

## Support

For issues or questions:
1. Check logs in console output
2. Review `TROUBLESHOOTING.md`
3. Verify all dependencies are installed
4. Ensure FFmpeg is properly configured

---

**Remember**: The more clips you rate, the better the AI becomes at finding highlights that match your preferences!
