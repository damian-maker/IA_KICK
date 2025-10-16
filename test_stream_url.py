"""
Test Stream URL
Quick script to test if a stream URL is accessible
"""

import sys
import ffmpeg
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_stream_url(url):
    """Test if a stream URL can be probed"""
    print("="*60)
    print(f"Testing Stream URL")
    print("="*60)
    print(f"URL: {url}")
    print("\nAttempting to probe stream...")
    print("This may take 10-30 seconds...\n")
    
    try:
        # Try to probe with timeout
        probe = ffmpeg.probe(url, timeout=30)
        
        print("✅ SUCCESS! Stream is accessible\n")
        
        # Display stream info
        print("Stream Information:")
        print("-" * 60)
        
        # Format info
        if 'format' in probe:
            fmt = probe['format']
            print(f"Format: {fmt.get('format_name', 'unknown')}")
            duration = float(fmt.get('duration', 0))
            if duration > 0:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                seconds = int(duration % 60)
                print(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                print("Duration: Unknown (possibly live stream)")
            print(f"Bitrate: {fmt.get('bit_rate', 'unknown')}")
        
        # Stream info
        if 'streams' in probe:
            print(f"\nStreams: {len(probe['streams'])}")
            
            for i, stream in enumerate(probe['streams']):
                codec_type = stream.get('codec_type', 'unknown')
                codec_name = stream.get('codec_name', 'unknown')
                
                print(f"\n  Stream #{i} ({codec_type}):")
                print(f"    Codec: {codec_name}")
                
                if codec_type == 'video':
                    width = stream.get('width', 'unknown')
                    height = stream.get('height', 'unknown')
                    fps = stream.get('r_frame_rate', 'unknown')
                    print(f"    Resolution: {width}x{height}")
                    print(f"    FPS: {fps}")
                
                elif codec_type == 'audio':
                    sample_rate = stream.get('sample_rate', 'unknown')
                    channels = stream.get('channels', 'unknown')
                    print(f"    Sample Rate: {sample_rate}")
                    print(f"    Channels: {channels}")
        
        print("\n" + "="*60)
        print("✅ This URL should work with the Kick Clip Generator!")
        print("="*60)
        return True
        
    except ffmpeg.Error as e:
        print("❌ FAILED! FFprobe error\n")
        error_msg = e.stderr.decode() if e.stderr else str(e)
        print("Error details:")
        print("-" * 60)
        print(error_msg)
        print("-" * 60)
        
        print("\nPossible causes:")
        print("1. URL is invalid or not accessible")
        print("2. Stream requires authentication")
        print("3. Network/firewall blocking access")
        print("4. Stream is offline or geo-restricted")
        
        print("\nTroubleshooting:")
        print("- Try opening the URL in VLC Media Player")
        print("- Check if URL works in a web browser")
        print("- Verify you have internet connection")
        print("- Try a different stream URL")
        
        return False
        
    except Exception as e:
        print(f"❌ FAILED! Unexpected error: {e}\n")
        
        print("Troubleshooting:")
        print("- Verify ffprobe is installed: ffprobe -version")
        print("- Check internet connection")
        print("- Try with a local video file first")
        
        return False


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("="*60)
        print("Stream URL Tester")
        print("="*60)
        print("\nUsage:")
        print("  python test_stream_url.py <stream_url>")
        print("\nExamples:")
        print('  python test_stream_url.py "https://kick.com/channel"')
        print('  python test_stream_url.py "https://example.com/stream.m3u8"')
        print('  python test_stream_url.py "C:\\path\\to\\video.mp4"')
        print("\nOr enter URL now:")
        url = input("\nStream URL: ").strip()
        
        if not url:
            print("No URL provided. Exiting.")
            return
    
    # Remove quotes if present
    url = url.strip('"').strip("'")
    
    # Test the URL
    success = test_stream_url(url)
    
    if success:
        print("\n✅ Ready to process with Kick Clip Generator!")
        print("\nRun:")
        print(f'  python main.py --url "{url}" --generate-clips')
    else:
        print("\n❌ Fix the issues above before processing this URL")
        print("\nFor more help, see: TROUBLESHOOTING.md")


if __name__ == "__main__":
    main()
