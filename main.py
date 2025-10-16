"""
Main entry point for Kick Clip Generator
Provides both CLI and GUI interfaces
"""

import argparse
import sys
import logging
from pathlib import Path
from kick_clip_generator import KickClipGenerator
from kick_api import KickAPI
from gradio_interface import GradioInterface
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Create necessary directories"""
    Path(config.TEMP_DIR).mkdir(exist_ok=True)
    Path(config.OUTPUT_DIR).mkdir(exist_ok=True)
    Path(config.MODEL_DIR).mkdir(exist_ok=True)
    logger.info("Directories initialized")


def cli_mode(args):
    """Run in command-line mode"""
    setup_directories()
    
    logger.info("Starting Kick Clip Generator in CLI mode")
    
    # Initialize components
    generator = KickClipGenerator(
        clip_duration=args.clip_duration,
        min_gap=args.min_gap
    )
    
    kick_api = KickAPI()
    
    # Handle Kick VODs specially (they require download via yt-dlp)
    stream_url = args.url
    temp_vod_file = None
    
    if 'kick.com' in stream_url and not stream_url.endswith(('.m3u8', '.mp4')):
        # Check if it's a VOD URL
        video_id = kick_api.extract_video_id_from_url(stream_url)
        
        if video_id:
            # It's a VOD - download it first using yt-dlp
            logger.info("Detected Kick VOD - downloading via yt-dlp...")
            temp_vod_file = Path(config.TEMP_DIR) / f"vod_{video_id}.mp4"
            
            # Convertir minutos a segundos para yt-dlp
            start_time_str = None
            end_time_str = None
            
            if args.start_minute is not None:
                start_secs = int(args.start_minute * 60)
                start_time_str = str(start_secs)
            if args.end_minute is not None:
                end_secs = int(args.end_minute * 60)
                end_time_str = str(end_secs)
                
            logger.info(f"Downloading VOD segment: {start_time_str or 'start'}s to {end_time_str or 'end'}s")
                
            if kick_api.download_vod_with_ytdlp(stream_url, str(temp_vod_file), start_time_str, end_time_str):
                stream_url = str(temp_vod_file)
                logger.info(f"VOD segment downloaded, processing: {stream_url}")
            else:
                logger.error("Could not download Kick VOD segment")
                return 1
        else:
            # It's a live stream - resolve URL
            logger.info("Resolving Kick live stream URL...")
            resolved_url = kick_api.resolve_kick_url(stream_url)
            if resolved_url:
                stream_url = resolved_url
                logger.info(f"Resolved to: {stream_url}")
            else:
                logger.error("Could not resolve Kick URL")
                return 1
    
    # Process stream
    logger.info(f"Processing stream: {stream_url}")
    
    def progress_callback(chunk_idx, current_time, total_duration):
        progress = (current_time / total_duration) * 100
        logger.info(f"Progress: {progress:.1f}% (chunk {chunk_idx}, {current_time:.0f}s / {total_duration:.0f}s)")
    
    try:
        # Enforce clip limits
        max_audio = min(args.max_audio_clips, config.MAX_CLIPS_PER_TYPE)
        max_video = min(args.max_video_clips, config.MAX_CLIPS_PER_TYPE)
        
        logger.info(f"Clip limits: {max_audio} audio, {max_video} video (max {config.MAX_TOTAL_CLIPS} total)")
        
        # Log time range if specified
        if args.start_minute is not None or args.end_minute is not None:
            start_str = f"{args.start_minute:.1f}" if args.start_minute is not None else "beginning"
            end_str = f"{args.end_minute:.1f}" if args.end_minute is not None else "end"
            logger.info(f"Time range: {start_str} to {end_str} minutes")
        
        audio_highlights, video_highlights = generator.process_stream(
            stream_url,
            progress_callback=progress_callback,
            max_audio_clips=max_audio,
            max_video_clips=max_video,
            start_minute=args.start_minute,
            end_minute=args.end_minute
        )
        
        logger.info(f"Found {len(audio_highlights)} audio highlights")
        logger.info(f"Found {len(video_highlights)} video highlights")
        
        # Display highlights
        print("\n" + "="*60)
        print("AUDIO HIGHLIGHTS")
        print("="*60)
        for idx, h in enumerate(audio_highlights, 1):
            print(f"{idx}. Time: {int(h.start_time//60)}:{int(h.start_time%60):02d} - Score: {h.score:.2f}")
        
        print("\n" + "="*60)
        print("VIDEO HIGHLIGHTS")
        print("="*60)
        for idx, h in enumerate(video_highlights, 1):
            print(f"{idx}. Time: {int(h.start_time//60)}:{int(h.start_time%60):02d} - Score: {h.score:.2f}")
        
        # Generate clips if requested
        if args.generate_clips:
            logger.info("Generating clips...")
            
            if args.type == 'audio':
                highlights = audio_highlights
            elif args.type == 'video':
                highlights = video_highlights
            else:  # both
                highlights = audio_highlights + video_highlights
            
            clips = generator.generate_clips(stream_url, highlights)
            
            print("\n" + "="*60)
            print(f"GENERATED {len(clips)} CLIPS")
            print("="*60)
            for clip in clips:
                print(f"- {Path(clip).name}")
            
            # Export metadata
            json_path = Path(config.OUTPUT_DIR) / "highlights.json"
            generator.export_highlights_json(audio_highlights, video_highlights, str(json_path))
            print(f"\nMetadata exported to: {json_path}")
        
        logger.info("Processing complete!")
        return 0
        
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        return 1
    finally:
        # Cleanup temporary VOD file if it was downloaded
        if temp_vod_file and Path(temp_vod_file).exists():
            try:
                Path(temp_vod_file).unlink()
                logger.info("Cleaned up temporary VOD file")
            except Exception as e:
                logger.warning(f"Could not delete temp VOD file: {e}")


def gui_mode(args):
    """Run in GUI mode with Gradio"""
    setup_directories()
    
    logger.info("Starting Kick Clip Generator in GUI mode")
    
    interface = GradioInterface()
    interface.launch(
        server_name=args.server_name or config.GRADIO_SERVER_NAME,
        server_port=args.port or config.GRADIO_SERVER_PORT,
        share=args.share or config.GRADIO_SHARE,
        show_error=True
    )
    
    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Kick Clip Generator - AI-powered highlight detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch GUI
  python main.py --gui
  
  # Process stream in CLI
  python main.py --url "https://kick.com/channel" --generate-clips
  
  # Process with custom settings
  python main.py --url "stream.m3u8" --clip-duration 45 --min-gap 15 --generate-clips
  
  # Process specific time range (minutes 10-30)
  python main.py --url "video.mp4" --start-minute 10 --end-minute 30 --generate-clips
  
  # GUI with custom port
  python main.py --gui --port 8080 --share
        """
    )
    
    # Mode selection
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch Gradio web interface (default mode)'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run in command-line mode'
    )
    
    # CLI arguments
    parser.add_argument(
        '--url',
        type=str,
        help='Stream URL (Kick URL or direct video URL)'
    )
    
    parser.add_argument(
        '--clip-duration',
        type=int,
        default=config.DEFAULT_CLIP_DURATION,
        help=f'Duration of generated clips in seconds (default: {config.DEFAULT_CLIP_DURATION})'
    )
    
    parser.add_argument(
        '--min-gap',
        type=int,
        default=config.MIN_GAP_BETWEEN_HIGHLIGHTS,
        help=f'Minimum gap between highlights in seconds (default: {config.MIN_GAP_BETWEEN_HIGHLIGHTS})'
    )
    
    parser.add_argument(
        '--generate-clips',
        action='store_true',
        help='Generate video clips from detected highlights'
    )
    
    parser.add_argument(
        '--type',
        choices=['audio', 'video', 'both'],
        default='both',
        help='Type of highlights to generate (default: both)'
    )
    
    parser.add_argument(
        '--max-audio-clips',
        type=int,
        default=10,
        help='Maximum number of audio clips to generate (1-25, default: 10)'
    )
    
    parser.add_argument(
        '--max-video-clips',
        type=int,
        default=10,
        help='Maximum number of video clips to generate (1-25, default: 10)'
    )
    
    parser.add_argument(
        '--start-minute',
        type=float,
        default=None,
        help='Start time in minutes (default: from beginning)'
    )
    
    parser.add_argument(
        '--end-minute',
        type=float,
        default=None,
        help='End time in minutes (default: until end)'
    )
    
    # GUI arguments
    parser.add_argument(
        '--server-name',
        type=str,
        help=f'Server name for Gradio (default: {config.GRADIO_SERVER_NAME})'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help=f'Port for Gradio server (default: {config.GRADIO_SERVER_PORT})'
    )
    
    parser.add_argument(
        '--share',
        action='store_true',
        help='Create public Gradio link'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.cli or args.url:
        if not args.url:
            parser.error("--url is required in CLI mode")
        return cli_mode(args)
    else:
        # Default to GUI mode
        return gui_mode(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
