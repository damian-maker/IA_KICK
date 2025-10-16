"""
Kick.com API utilities for extracting stream information
Handles Kick-specific URL parsing and video URL extraction
"""

import re
import json
import logging
import subprocess
import sys
from typing import Optional, Dict, Tuple
from kick_clip_generator import RetrySession

logger = logging.getLogger(__name__)


class KickAPI:
    """Interface for Kick.com API"""
    
    def __init__(self):
        self.session = RetrySession()
        self.base_url = "https://kick.com/api/v2"
    
    def extract_channel_from_url(self, url: str) -> Optional[str]:
        """Extract channel name from Kick URL"""
        # First check if it's a video URL (channelname/videos/id format)
        video_with_channel = re.search(r'kick\.com/([^/]+)/videos/', url)
        if video_with_channel:
            return video_with_channel.group(1)
        
        # Match channel URL: kick.com/channelname
        channel_pattern = r'kick\.com/([^/\?]+)(?:\?|$)'
        match = re.search(channel_pattern, url)
        if match:
            channel = match.group(1)
            # Exclude 'video' as it's not a channel
            if channel != 'video':
                return channel
        
        return None
    
    def extract_video_id_from_url(self, url: str) -> Optional[str]:
        """Extract video ID from Kick VOD URL"""
        # Match video URL formats:
        # - kick.com/video/video_id
        # - kick.com/channelname/videos/video_id
        # - kick.com/channelname?video=video_id
        patterns = [
            r'kick\.com/video/([a-f0-9\-]+)',
            r'kick\.com/[^/]+/videos/([a-f0-9\-]+)',  # New format: channelname/videos/id
            r'kick\.com/[^/]+\?.*video=([a-f0-9\-]+)',
            r'kick\.com/\?video=([a-f0-9\-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_channel_info(self, channel_name: str) -> Optional[Dict]:
        """Get channel information from Kick API"""
        try:
            url = f"{self.base_url}/channels/{channel_name}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get channel info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return None
    
    def get_livestream_url(self, channel_name: str) -> Optional[str]:
        """Get current livestream URL for a channel"""
        try:
            channel_info = self.get_channel_info(channel_name)
            
            if not channel_info:
                return None
            
            # Check if channel is live
            if not channel_info.get('livestream'):
                logger.warning(f"Channel {channel_name} is not currently live")
                return None
            
            livestream = channel_info['livestream']
            
            # Get playback URL
            playback_url = livestream.get('playback_url')
            
            if playback_url:
                logger.info(f"Found livestream URL: {playback_url}")
                return playback_url
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting livestream URL: {e}")
            return None
    
    def get_vod_url(self, video_id: str) -> Optional[str]:
        """Get VOD (Video on Demand) URL"""
        try:
            url = f"{self.base_url}/videos/{video_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                video_url = data.get('source')
                
                if video_url:
                    logger.info(f"Found VOD URL: {video_url}")
                    return video_url
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting VOD URL: {e}")
            return None
    
    def check_ytdlp_available(self) -> bool:
        """Check if yt-dlp is installed"""
        try:
            subprocess.run(['yt-dlp', '--version'], 
                         capture_output=True, 
                         check=True, 
                         timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def download_vod_with_ytdlp(self, url: str, output_path: str, start_time=None, end_time=None) -> bool:
        """Download VOD using yt-dlp with time range support"""
        try:
            logger.info(f"Downloading VOD using yt-dlp to: {output_path}")
            if start_time and end_time:
                logger.info(f"Downloading segment from {start_time}s to {end_time}s")
            
            # Base command with optimized settings
            command = [
                'yt-dlp',
                '--impersonate', 'chrome',
                '-f', 'best',
                '-N', '16',                  # 16 fragmentos concurrentes para descarga más rápida
                '--retries', '10',
                '--fragment-retries', '50',
                '--retry-sleep', '3',
                '--no-part',                 # escribir directamente al archivo final
                '--no-mtime',
                '--concurrent-fragments', '16'  # máximo paralelismo
            ]
            
            # Agregar opciones de tiempo si se especifican
            if start_time is not None:
                download_range = f"*{start_time}-{end_time if end_time else 'inf'}"
                command.extend(['--download-sections', download_range])
                
            # Agregar el resto de las opciones
            command.extend([
                '-o', output_path,
                '--newline',
                '--progress',
                url
            ])
            
            logger.info("Ejecutando comando yt-dlp...")
            
            # Intentar la descarga hasta 2 veces
            for attempt in range(2):
                if attempt > 0:
                    logger.info(f"Reintentando descarga (intento {attempt + 1}/2)")
                
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Mostrar progreso
                last_progress = ""
                for line in process.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if '[download]' in line and '%' in line:
                        if line != last_progress:
                            logger.info(line)
                            last_progress = line
                    elif 'ERROR' in line or 'WARNING' in line:
                        logger.warning(line)
                
                return_code = process.wait()
                if return_code == 0:
                    logger.info("Descarga completada exitosamente")
                    return True
                else:
                    logger.error(f"yt-dlp falló con código de salida: {return_code}")
            
            logger.error("La descarga falló después de todos los intentos")
            return False
                
        except subprocess.TimeoutExpired:
            logger.error("Download timed out")
            return False
        except Exception as e:
            logger.error(f"Error downloading VOD: {e}")
            return False
    
    def get_stream_with_ytdlp(self, url: str) -> Optional[Tuple[str, Dict]]:
        """Use yt-dlp to extract stream URL with proper authentication"""
        try:
            logger.info("Attempting to extract stream URL using yt-dlp with impersonation...")
            
            # Run yt-dlp to get stream info with impersonation for Kick
            # Impersonation is required for Kick to bypass 403 errors
            result = subprocess.run(
                ['yt-dlp', '--impersonate', 'chrome', '-f', 'best', '-g', '--get-url', url],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout.strip():
                stream_url = result.stdout.strip().split('\n')[0]
                logger.info(f"yt-dlp extracted URL: {stream_url[:100]}...")
                
                # Get additional info
                info_result = subprocess.run(
                    ['yt-dlp', '--impersonate', 'chrome', '-j', url],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                info = {}
                if info_result.returncode == 0:
                    try:
                        info = json.loads(info_result.stdout)
                    except:
                        pass
                
                return stream_url, info
            else:
                logger.error(f"yt-dlp failed: {result.stderr}")
                return None
                
        except FileNotFoundError:
            logger.error("yt-dlp not found. Install with: pip install yt-dlp")
            return None
        except Exception as e:
            logger.error(f"Error using yt-dlp: {e}")
            return None
    
    def resolve_kick_url(self, url: str) -> Optional[str]:
        """
        Resolve a Kick URL to a playable video URL
        Handles both livestreams and VODs
        Uses yt-dlp for authentication when needed
        """
        # If it's already a direct video URL, check if it's accessible
        if url.endswith('.m3u8') or url.endswith('.mp4'):
            # If it's a Kick stream URL, it likely needs authentication
            if 'kick.com' in url or 'stream.kick.com' in url:
                logger.warning("Direct Kick stream URL detected - may require authentication")
                logger.info("Attempting to use yt-dlp for authentication...")
                
                if self.check_ytdlp_available():
                    # For direct URLs, we need the original Kick page URL
                    logger.error("Direct stream URLs from Kick require the original page URL")
                    logger.error("Please provide the Kick channel URL instead (e.g., https://kick.com/channelname)")
                    return None
                else:
                    logger.error("yt-dlp is required for Kick streams")
                    logger.error("Install with: pip install yt-dlp")
                    return None
            else:
                # Non-Kick URL, return as-is
                return url
        
        # For Kick URLs, try yt-dlp first (handles authentication for both live and VOD)
        if 'kick.com' in url:
            if self.check_ytdlp_available():
                logger.info("Using yt-dlp to extract stream URL (works for both live and VOD)...")
                result = self.get_stream_with_ytdlp(url)
                if result:
                    stream_url, info = result
                    # Check if it's a live stream or VOD
                    is_live = info.get('is_live', False)
                    if is_live:
                        logger.info("Detected LIVE stream")
                    else:
                        logger.info("Detected VOD (past stream)")
                    return stream_url
                else:
                    logger.warning("yt-dlp extraction failed, trying API fallback...")
            else:
                logger.warning("yt-dlp not available - Kick streams may not work")
                logger.info("Install yt-dlp for better Kick support: pip install yt-dlp")
        
        # Fallback to API method (may not work for protected streams)
        # First, check if it's a video URL
        video_id = self.extract_video_id_from_url(url)
        if video_id:
            logger.info(f"Detected VOD URL with video ID: {video_id}")
            vod_url = self.get_vod_url(video_id)
            if vod_url:
                return vod_url
        
        # Try to extract channel name
        channel_name = self.extract_channel_from_url(url)
        if not channel_name:
            logger.error(f"Could not extract channel or video ID from URL: {url}")
            return None
        
        # Try to get livestream
        logger.info(f"Checking if channel '{channel_name}' is live...")
        stream_url = self.get_livestream_url(channel_name)
        if stream_url:
            return stream_url
        
        logger.error(f"Could not resolve Kick URL: {url}")
        logger.error("For Kick streams, yt-dlp is recommended for best compatibility")
        logger.error("Install with: pip install yt-dlp")
        return None
    
    def get_stream_metadata(self, channel_name: str) -> Optional[Dict]:
        """Get detailed stream metadata"""
        try:
            channel_info = self.get_channel_info(channel_name)
            
            if not channel_info:
                return None
            
            livestream = channel_info.get('livestream', {})
            
            metadata = {
                'channel': channel_name,
                'title': livestream.get('session_title', 'Unknown'),
                'category': livestream.get('category', {}).get('name', 'Unknown'),
                'viewers': livestream.get('viewer_count', 0),
                'is_live': livestream.get('is_live', False),
                'started_at': livestream.get('created_at'),
                'thumbnail': livestream.get('thumbnail', {}).get('url'),
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting stream metadata: {e}")
            return None


def test_kick_api():
    """Test the Kick API functionality"""
    api = KickAPI()
    
    # Test URL patterns
    test_urls = [
        "https://kick.com/channelname",  # Live stream
        "https://kick.com/video/abc123-def456",  # VOD
        "https://example.com/stream.m3u8"  # External stream
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        # Test channel extraction
        channel = api.extract_channel_from_url(url)
        print(f"Extracted channel: {channel}")
        
        # Test video ID extraction
        video_id = api.extract_video_id_from_url(url)
        print(f"Extracted video ID: {video_id}")
        
        # Test URL resolution
        if not url.endswith('.m3u8'):
            resolved = api.resolve_kick_url(url)
            print(f"Resolved URL: {resolved}")
            
            # Get metadata if it's a channel
            if channel:
                metadata = api.get_stream_metadata(channel)
                if metadata:
                    print(f"Metadata: {json.dumps(metadata, indent=2)}")


if __name__ == "__main__":
    test_kick_api()