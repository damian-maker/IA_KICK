"""
Example usage scripts for Kick Clip Generator
Demonstrates various ways to use the system
"""

from kick_clip_generator import KickClipGenerator
from kick_api import KickAPI
import logging

logging.basicConfig(level=logging.INFO)


def example_1_basic_processing():
    """Example 1: Basic stream processing"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Stream Processing")
    print("="*60)
    
    # Initialize generator
    generator = KickClipGenerator()
    
    # Process a stream (replace with actual URL)
    stream_url = "https://example.com/stream.m3u8"
    
    print(f"Processing: {stream_url}")
    
    # Process and get highlights
    audio_highlights, video_highlights = generator.process_stream(stream_url)
    
    print(f"\nResults:")
    print(f"- Audio highlights: {len(audio_highlights)}")
    print(f"- Video highlights: {len(video_highlights)}")
    
    # Display top 3 audio highlights
    print("\nTop 3 Audio Highlights:")
    for i, h in enumerate(audio_highlights[:3], 1):
        print(f"{i}. Time: {h.start_time:.1f}s, Score: {h.score:.2f}")


def example_2_custom_settings():
    """Example 2: Custom settings"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Settings")
    print("="*60)
    
    # Create generator with custom settings
    generator = KickClipGenerator(
        clip_duration=45,  # 45-second clips
        min_gap=20         # 20 seconds between highlights
    )
    
    # Custom chunk processing
    generator.processor.chunk_duration = 60  # 60-second chunks
    generator.processor.overlap = 10         # 10-second overlap
    
    print("Custom settings:")
    print(f"- Clip duration: {generator.clip_duration}s")
    print(f"- Min gap: {generator.min_gap}s")
    print(f"- Chunk duration: {generator.processor.chunk_duration}s")


def example_3_kick_url_resolution():
    """Example 3: Resolving Kick URLs"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Kick URL Resolution")
    print("="*60)
    
    api = KickAPI()
    
    # Example Kick URLs
    kick_urls = [
        "https://kick.com/channelname",
        "https://kick.com/video/12345"
    ]
    
    for url in kick_urls:
        print(f"\nOriginal URL: {url}")
        
        # Extract channel
        channel = api.extract_channel_from_url(url)
        print(f"Channel: {channel}")
        
        # Get metadata (if channel is live)
        if channel:
            metadata = api.get_stream_metadata(channel)
            if metadata:
                print(f"Title: {metadata.get('title')}")
                print(f"Category: {metadata.get('category')}")
                print(f"Viewers: {metadata.get('viewers')}")


def example_4_generate_clips():
    """Example 4: Generate clips from highlights"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Generate Clips")
    print("="*60)
    
    generator = KickClipGenerator()
    stream_url = "https://example.com/stream.m3u8"
    
    # Process stream
    audio_highlights, video_highlights = generator.process_stream(stream_url)
    
    # Generate clips from audio highlights only
    print("\nGenerating clips from audio highlights...")
    audio_clips = generator.generate_clips(
        stream_url, 
        audio_highlights,
        prefix='audio_highlight'
    )
    print(f"Generated {len(audio_clips)} audio clips")
    
    # Generate clips from video highlights only
    print("\nGenerating clips from video highlights...")
    video_clips = generator.generate_clips(
        stream_url,
        video_highlights,
        prefix='video_highlight'
    )
    print(f"Generated {len(video_clips)} video clips")
    
    # Export metadata
    generator.export_highlights_json(audio_highlights, video_highlights)
    print("\nMetadata exported to highlights.json")


def example_5_progress_tracking():
    """Example 5: Progress tracking"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Progress Tracking")
    print("="*60)
    
    generator = KickClipGenerator()
    stream_url = "https://example.com/stream.m3u8"
    
    # Define progress callback
    def progress_callback(chunk_idx, current_time, total_duration):
        progress = (current_time / total_duration) * 100
        bar_length = 40
        filled = int(bar_length * current_time / total_duration)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\rProgress: [{bar}] {progress:.1f}% (Chunk {chunk_idx})", end='', flush=True)
    
    # Process with progress tracking
    audio_highlights, video_highlights = generator.process_stream(
        stream_url,
        progress_callback=progress_callback
    )
    
    print("\n\nProcessing complete!")


def example_6_feature_analysis():
    """Example 6: Analyzing extracted features"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Feature Analysis")
    print("="*60)
    
    from kick_clip_generator import AudioAnalyzer, VideoAnalyzer
    
    audio_analyzer = AudioAnalyzer()
    video_analyzer = VideoAnalyzer()
    
    # Example: Extract features from a video file
    video_path = "example_video.mp4"
    
    print(f"Analyzing: {video_path}")
    
    # Extract audio features
    print("\nExtracting audio features...")
    audio_features = audio_analyzer.extract_audio_features(video_path)
    if audio_features:
        print("Audio features:")
        for key, value in list(audio_features.items())[:5]:
            print(f"  {key}: {value:.4f}")
    
    # Extract video features
    print("\nExtracting video features...")
    video_features = video_analyzer.extract_video_features(video_path)
    if video_features:
        print("Video features:")
        for key, value in video_features.items():
            print(f"  {key}: {value:.4f}")
    
    # Calculate scores
    audio_score = audio_analyzer.detect_audio_highlights(audio_features)
    video_score = video_analyzer.detect_video_highlights(video_features)
    
    print(f"\nScores:")
    print(f"  Audio score: {audio_score:.2f}")
    print(f"  Video score: {video_score:.2f}")


def example_7_ml_model_training():
    """Example 7: ML model training and improvement"""
    print("\n" + "="*60)
    print("EXAMPLE 7: ML Model Training")
    print("="*60)
    
    from kick_clip_generator import MLHighlightModel
    
    model = MLHighlightModel()
    
    # Check training data
    audio_samples = len(model.training_data['audio']['features'])
    video_samples = len(model.training_data['video']['features'])
    
    print(f"Current training data:")
    print(f"  Audio samples: {audio_samples}")
    print(f"  Video samples: {video_samples}")
    
    # Add sample training data (example)
    sample_features = {
        'feature1': 0.5,
        'feature2': 0.8,
        'feature3': 0.3
    }
    
    print("\nAdding training sample...")
    model.add_training_sample(sample_features, score=7.5, feature_type='audio')
    
    # Retrain model
    if audio_samples >= 10:
        print("Retraining model...")
        model.retrain()
        print("Model retrained successfully!")
    else:
        print(f"Need {10 - audio_samples} more samples to train model")


def example_8_batch_processing():
    """Example 8: Batch processing multiple streams"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Batch Processing")
    print("="*60)
    
    generator = KickClipGenerator()
    
    # List of streams to process
    stream_urls = [
        "https://example.com/stream1.m3u8",
        "https://example.com/stream2.m3u8",
        "https://example.com/stream3.m3u8"
    ]
    
    results = []
    
    for idx, url in enumerate(stream_urls, 1):
        print(f"\nProcessing stream {idx}/{len(stream_urls)}")
        print(f"URL: {url}")
        
        try:
            audio_h, video_h = generator.process_stream(url)
            
            results.append({
                'url': url,
                'audio_highlights': len(audio_h),
                'video_highlights': len(video_h),
                'status': 'success'
            })
            
            # Generate clips
            clips = generator.generate_clips(url, audio_h + video_h)
            print(f"Generated {len(clips)} clips")
            
        except Exception as e:
            print(f"Error: {e}")
            results.append({
                'url': url,
                'status': 'failed',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    
    for result in results:
        status = "✅" if result['status'] == 'success' else "❌"
        print(f"{status} {result['url']}")
        if result['status'] == 'success':
            print(f"   Audio: {result['audio_highlights']}, Video: {result['video_highlights']}")


def example_9_error_handling():
    """Example 9: Error handling demonstration"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Error Handling")
    print("="*60)
    
    from kick_clip_generator import RetrySession
    
    session = RetrySession(max_retries=3, backoff_factor=2)
    
    # Example: Handling 403 errors
    test_url = "https://httpstat.us/403"
    
    print(f"Testing error handling with: {test_url}")
    print("This will demonstrate automatic retry with backoff...")
    
    try:
        response = session.get(test_url)
        print(f"Response: {response.status_code}")
    except Exception as e:
        print(f"Failed after retries: {e}")
        print("The system tried multiple times with exponential backoff")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("KICK CLIP GENERATOR - EXAMPLE USAGE")
    print("="*60)
    
    examples = [
        ("Basic Processing", example_1_basic_processing),
        ("Custom Settings", example_2_custom_settings),
        ("Kick URL Resolution", example_3_kick_url_resolution),
        ("Generate Clips", example_4_generate_clips),
        ("Progress Tracking", example_5_progress_tracking),
        ("Feature Analysis", example_6_feature_analysis),
        ("ML Model Training", example_7_ml_model_training),
        ("Batch Processing", example_8_batch_processing),
        ("Error Handling", example_9_error_handling)
    ]
    
    print("\nAvailable examples:")
    for idx, (name, _) in enumerate(examples, 1):
        print(f"{idx}. {name}")
    
    print("\nNote: Some examples require actual stream URLs to work.")
    print("Replace 'https://example.com/stream.m3u8' with real URLs.")
    
    # Uncomment to run specific examples:
    # example_2_custom_settings()
    # example_3_kick_url_resolution()
    # example_7_ml_model_training()


if __name__ == "__main__":
    main()
