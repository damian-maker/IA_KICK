"""
Kick Stream Clip Generator with ML-based Highlight Detection
Processes streams in chunks without downloading full videos
"""

import os
import json
import time
import logging
import numpy as np
import cv2
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import threading
from queue import Queue
import pickle
from pathlib import Path
import config

# Audio processing
import librosa
import soundfile as sf
from scipy import signal
from scipy.stats import zscore

# ML and data processing
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib

# Video processing
import ffmpeg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Highlight:
    """Represents a detected highlight segment"""
    start_time: float
    end_time: float
    score: float
    type: str  # 'audio' or 'video'
    features: Dict
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class RetrySession:
    """HTTP session with retry logic and 403 error handling"""
    
    def __init__(self, max_retries=5, backoff_factor=2, timeout=30):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://kick.com/',
            'Origin': 'https://kick.com'
        })
    
    def get(self, url, **kwargs):
        """GET request with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout, **kwargs)
                
                if response.status_code == 403:
                    wait_time = self.backoff_factor ** attempt
                    logger.warning(f"403 error, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    
                    # Rotate user agent
                    user_agents = [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                    ]
                    self.session.headers['User-Agent'] = user_agents[attempt % len(user_agents)]
                    continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed after {self.max_retries} attempts: {e}")
                    raise
                wait_time = self.backoff_factor ** attempt
                logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        raise Exception("Max retries exceeded")


class StreamProcessor:
    """Processes video streams in chunks without full download"""
    
    def __init__(self, chunk_duration=45, overlap=3):  # Chunks más grandes y menos solapamiento para mejor rendimiento
        self.chunk_duration = chunk_duration  # seconds
        self.overlap = overlap  # seconds overlap between chunks
        self.session = RetrySession()
        self.temp_dir = Path("temp_chunks")
        self.temp_dir.mkdir(exist_ok=True)
        self._verify_ffmpeg()
    
    def _verify_ffmpeg(self):
        """Verify ffmpeg and ffprobe are available"""
        import subprocess
        try:
            # Check ffmpeg
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, 
                         check=True, 
                         timeout=5)
            logger.info("FFmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("FFmpeg not found in PATH - video processing may fail")
        
        try:
            # Check ffprobe
            subprocess.run(['ffprobe', '-version'], 
                         capture_output=True, 
                         check=True, 
                         timeout=5)
            logger.info("FFprobe is available")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.error("FFprobe not found in PATH - stream analysis will fail")
            logger.error("Please ensure FFmpeg is properly installed with ffprobe")
    
    def get_stream_info(self, stream_url: str) -> Dict:
        """Extract stream metadata"""
        try:
            # Try to probe the stream with timeout
            probe = ffmpeg.probe(stream_url, timeout=30)
            
            # Find video and audio streams
            video_info = None
            audio_info = None
            
            for stream in probe.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_info:
                    video_info = stream
                elif stream.get('codec_type') == 'audio' and not audio_info:
                    audio_info = stream
            
            if not video_info:
                logger.error("No video stream found in the source")
                return None
            
            # Get duration from format or video stream
            duration = float(probe.get('format', {}).get('duration', 0))
            
            # If duration is 0 or not available, try to estimate or use a default
            if duration == 0:
                logger.warning("Duration not available, will process in chunks until end")
                duration = 28800  # Default to 8 hours for live streams
            
            # Build info dict with safe defaults
            info = {
                'duration': duration,
                'video_codec': video_info.get('codec_name', 'unknown'),
                'width': int(video_info.get('width', 1920)),
                'height': int(video_info.get('height', 1080)),
            }
            
            # Safely parse FPS
            try:
                fps_str = video_info.get('r_frame_rate', '30/1')
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    info['fps'] = float(num) / float(den)
                else:
                    info['fps'] = float(fps_str)
            except:
                info['fps'] = 30.0  # Default FPS
            
            # Add audio info if available
            if audio_info:
                info['audio_codec'] = audio_info.get('codec_name', 'unknown')
            else:
                logger.warning("No audio stream found, audio analysis will be skipped")
                info['audio_codec'] = None
            
            logger.info(f"Stream info: {info['width']}x{info['height']} @ {info['fps']:.2f}fps, duration: {duration:.1f}s")
            return info
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"FFprobe error: {error_msg}")
            logger.error("Make sure ffprobe is installed and in your PATH")
            logger.error(f"Stream URL: {stream_url}")
            return None
        except Exception as e:
            logger.error(f"Failed to get stream info: {e}")
            logger.error(f"Stream URL: {stream_url}")
            return None
    
    def download_chunk(self, stream_url: str, start_time: float, duration: float, output_path: str) -> bool:
        """Download a specific chunk of the stream"""
        try:
            # Use ffmpeg to extract chunk without downloading full video
            stream = ffmpeg.input(stream_url, ss=start_time, t=duration)
            stream = ffmpeg.output(stream, output_path, 
                                 codec='copy',
                                 loglevel='error',
                                 **{'avoid_negative_ts': 'make_zero'})
            ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
            return True
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error downloading chunk: {e.stderr.decode()}")
            return False
        except Exception as e:
            logger.error(f"Failed to download chunk: {e}")
            return False
    
    def process_stream_chunks(self, stream_url: str, callback=None, start_minute=None, end_minute=None):
        """Generator that yields processed chunks
        
        Args:
            stream_url: URL of the stream to process
            callback: Optional progress callback
            start_minute: Start time in minutes (None = from beginning)
            end_minute: End time in minutes (None = until end)
        """
        info = self.get_stream_info(stream_url)
        if not info:
            logger.error("Could not get stream info")
            return
        
        duration = info['duration']
        
        # Convert minutes to seconds
        start_time_sec = (start_minute * 60) if start_minute is not None else 0
        end_time_sec = (end_minute * 60) if end_minute is not None else duration
        
        # Validate time range
        if start_time_sec < 0:
            logger.warning(f"Start time cannot be negative, using 0")
            start_time_sec = 0
        
        if end_time_sec > duration:
            logger.warning(f"End time ({end_time_sec}s) exceeds video duration ({duration}s), using full duration")
            end_time_sec = duration
        
        if start_time_sec >= end_time_sec:
            logger.error(f"Invalid time range: start ({start_time_sec}s) >= end ({end_time_sec}s)")
            return
        
        # Calculate effective duration to process
        effective_duration = end_time_sec - start_time_sec
        
        # Enforce maximum stream duration to prevent memory issues
        if effective_duration > config.MAX_STREAM_DURATION:
            logger.warning(f"Requested duration ({effective_duration}s) exceeds maximum ({config.MAX_STREAM_DURATION}s). Processing first {config.MAX_STREAM_DURATION}s only.")
            end_time_sec = start_time_sec + config.MAX_STREAM_DURATION
            effective_duration = config.MAX_STREAM_DURATION
        
        logger.info(f"Processing stream: {effective_duration}s duration (from {start_time_sec}s to {end_time_sec}s), {int(effective_duration/self.chunk_duration)} chunks estimated")
        
        current_time = start_time_sec
        chunk_index = 0
        
        while current_time < end_time_sec:
            chunk_path = self.temp_dir / f"chunk_{chunk_index}.mp4"
            
            # Calculate chunk duration (may be shorter for last chunk)
            chunk_dur = min(self.chunk_duration, end_time_sec - current_time)
            
            # Download chunk
            success = self.download_chunk(
                stream_url, 
                current_time, 
                chunk_dur,
                str(chunk_path)
            )
            
            if success and chunk_path.exists():
                yield {
                    'path': str(chunk_path),
                    'start_time': current_time,
                    'end_time': min(current_time + chunk_dur, end_time_sec),
                    'index': chunk_index
                }
                
                if callback:
                    callback(chunk_index, current_time, end_time_sec)
            
            current_time += (self.chunk_duration - self.overlap)
            chunk_index += 1
    
    def cleanup(self):
        """Remove temporary chunk files (but preserve VOD files)"""
        try:
            # Only delete chunk files, not VOD files which are needed for clip generation
            for file in self.temp_dir.glob("chunk_*.mp4"):
                file.unlink()
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


class AudioAnalyzer:
    """Analyzes audio for exciting moments"""
    
    def __init__(self):
        self.sample_rate = 16000  # Reducido para mejorar rendimiento manteniendo calidad aceptable
    
    def extract_audio_features(self, video_path: str) -> Optional[Dict]:
        """Extract audio features from video chunk"""
        try:
            # Extract audio using ffmpeg
            audio_path = video_path.replace('.mp4', '_audio.wav')
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, audio_path, 
                                 acodec='pcm_s16le', 
                                 ac=1, 
                                 ar=self.sample_rate,
                                 loglevel='error')
            ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Extract features
            features = {}
            
            # 1. Volume/Energy analysis
            rms = librosa.feature.rms(y=y)[0]
            features['rms_mean'] = float(np.mean(rms))
            features['rms_std'] = float(np.std(rms))
            features['rms_max'] = float(np.max(rms))
            
            # 2. Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            features['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            # 3. Zero crossing rate (speech/excitement indicator)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zcr_mean'] = float(np.mean(zcr))
            features['zcr_std'] = float(np.std(zcr))
            
            # 4. Tempo and beat strength
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            features['beat_strength'] = float(len(beats) / (len(y) / sr))
            
            # 5. Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features['rolloff_mean'] = float(np.mean(rolloff))
            
            # 6. MFCC (voice characteristics)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(5):  # First 5 MFCCs
                features[f'mfcc_{i}_mean'] = float(np.mean(mfccs[i]))
            
            # 7. Loudness variation (excitement indicator)
            loudness = librosa.amplitude_to_db(rms, ref=np.max)
            features['loudness_variance'] = float(np.var(loudness))
            
            # 8. High frequency energy (screaming/excitement)
            high_freq_energy = np.sum(np.abs(librosa.stft(y))[:1000, :])
            features['high_freq_energy'] = float(high_freq_energy)
            
            # Cleanup
            os.remove(audio_path)
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return None
    
    def detect_audio_highlights(self, features: Dict, threshold_percentile=75) -> float:
        """Calculate highlight score based on audio features"""
        if not features:
            return 0.0
        
        # Weighted scoring
        score = 0.0
        
        # High energy/volume
        score += features.get('rms_mean', 0) * 2.0
        score += features.get('rms_std', 0) * 1.5
        
        # Voice excitement
        score += features.get('zcr_mean', 0) * 1.0
        score += features.get('spectral_centroid_mean', 0) / 1000.0
        
        # Loudness variation
        score += features.get('loudness_variance', 0) * 0.5
        
        # High frequency energy (excitement)
        score += features.get('high_freq_energy', 0) / 1e9
        
        return float(score)


class VideoAnalyzer:
    """Analyzes video for visual highlights"""
    
    def __init__(self):
        self.frame_skip = 10  # Aumentado para procesar menos frames y mejorar rendimiento
    
    def extract_video_features(self, video_path: str) -> Optional[Dict]:
        """Extract video features from chunk"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            features = {
                'motion_scores': [],
                'brightness_values': [],
                'color_variance': [],
                'edge_density': []
            }
            
            prev_frame = None
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Skip frames for performance
                if frame_idx % self.frame_skip != 0:
                    frame_idx += 1
                    continue
                
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 1. Motion detection
                if prev_frame is not None:
                    motion = cv2.absdiff(prev_frame, gray)
                    motion_score = np.mean(motion)
                    features['motion_scores'].append(float(motion_score))
                
                prev_frame = gray.copy()
                
                # 2. Brightness
                brightness = np.mean(gray)
                features['brightness_values'].append(float(brightness))
                
                # 3. Color variance (visual complexity)
                color_var = np.var(frame)
                features['color_variance'].append(float(color_var))
                
                # 4. Edge density (action indicator)
                edges = cv2.Canny(gray, 100, 200)
                edge_density = np.sum(edges > 0) / edges.size
                features['edge_density'].append(float(edge_density))
                
                frame_idx += 1
            
            cap.release()
            
            # Aggregate features
            aggregated = {
                'motion_mean': float(np.mean(features['motion_scores'])) if features['motion_scores'] else 0.0,
                'motion_std': float(np.std(features['motion_scores'])) if features['motion_scores'] else 0.0,
                'motion_max': float(np.max(features['motion_scores'])) if features['motion_scores'] else 0.0,
                'brightness_mean': float(np.mean(features['brightness_values'])) if features['brightness_values'] else 0.0,
                'brightness_std': float(np.std(features['brightness_values'])) if features['brightness_values'] else 0.0,
                'color_variance_mean': float(np.mean(features['color_variance'])) if features['color_variance'] else 0.0,
                'edge_density_mean': float(np.mean(features['edge_density'])) if features['edge_density'] else 0.0,
                'edge_density_std': float(np.std(features['edge_density'])) if features['edge_density'] else 0.0,
            }
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {e}")
            return None
    
    def detect_video_highlights(self, features: Dict) -> float:
        """Calculate highlight score based on video features"""
        if not features:
            return 0.0
        
        score = 0.0
        
        # High motion = action
        score += features.get('motion_mean', 0) * 2.0
        score += features.get('motion_std', 0) * 1.5
        
        # Edge density = visual complexity/action
        score += features.get('edge_density_mean', 0) * 100.0
        score += features.get('edge_density_std', 0) * 50.0
        
        # Color variance = visual interest
        score += features.get('color_variance_mean', 0) / 1000.0
        
        return float(score)


class MLHighlightModel:
    """Machine learning model that improves over time"""
    
    def __init__(self, model_path='models/highlight_model.pkl'):
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(exist_ok=True)
        
        self.audio_model = None
        self.video_model = None
        self.audio_scaler = StandardScaler()
        self.video_scaler = StandardScaler()
        self.audio_scaler_fitted = False
        self.video_scaler_fitted = False
        
        self.training_data = {
            'audio': {'features': [], 'scores': []},
            'video': {'features': [], 'scores': []}
        }
        
        self.load_model()
    
    def load_model(self):
        """Load existing model or create new one"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.audio_model = data['audio_model']
                    self.video_model = data['video_model']
                    self.audio_scaler = data['audio_scaler']
                    self.video_scaler = data['video_scaler']
                    self.training_data = data['training_data']
                    
                    # Store expected feature counts for validation
                    self.expected_audio_features = data.get('audio_feature_count', None)
                    self.expected_video_features = data.get('video_feature_count', None)
                    
                    # Mark scalers as fitted if they have been trained
                    self.audio_scaler_fitted = len(self.training_data['audio']['features']) >= 10
                    self.video_scaler_fitted = len(self.training_data['video']['features']) >= 10
                    
                logger.info("Loaded existing ML model")
            else:
                self.audio_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)
                self.video_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)
                self.expected_audio_features = None
                self.expected_video_features = None
                self.audio_scaler_fitted = False
                self.video_scaler_fitted = False
                logger.info("Created new ML model")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.audio_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)
            self.video_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)
            self.expected_audio_features = None
            self.expected_video_features = None
            self.audio_scaler_fitted = False
            self.video_scaler_fitted = False
    
    def save_model(self):
        """Save model to disk"""
        try:
            data = {
                'audio_model': self.audio_model,
                'video_model': self.video_model,
                'audio_scaler': self.audio_scaler,
                'video_scaler': self.video_scaler,
                'training_data': self.training_data,
                'audio_feature_count': self.expected_audio_features,
                'video_feature_count': self.expected_video_features
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info("Saved ML model")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def __init__(self, model_path='models/highlight_model.pkl'):
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(exist_ok=True)
        
        self.audio_model = None
        self.video_model = None
        self.audio_scaler = StandardScaler()
        self.video_scaler = StandardScaler()
        self.audio_scaler_fitted = False
        self.video_scaler_fitted = False
        
        self.training_data = {
            'audio': {'features': [], 'scores': []},
            'video': {'features': [], 'scores': []}
        }
        
        self.cache = {}  # Cache para predicciones
        self.load_model()
        
    def predict_audio_score(self, features: Dict) -> float:
        """Predict highlight score for audio features with caching"""
        try:
            # Generar clave de cache basada en características
            cache_key = hash(str(sorted(features.items())))
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            feature_vector = self._dict_to_vector(features)
            
            # Check if scaler is fitted and we have enough training data
            if not self.audio_scaler_fitted or len(self.training_data['audio']['features']) < 10:
                # Not enough training data or scaler not fitted, use heuristic
                score = 0.0
            else:
                # Check for feature count mismatch
                if hasattr(self, 'expected_audio_features') and self.expected_audio_features is not None and len(feature_vector) != self.expected_audio_features:
                    logger.warning(f"Audio feature mismatch: got {len(feature_vector)}, expected {self.expected_audio_features}. Resetting model.")
                    self._reset_audio_model()
                    score = 0.0
                else:
                    scaled = self.audio_scaler.transform([feature_vector])
                    score = self.audio_model.predict(scaled)[0]
            
            # Almacenar en caché
            self.cache[cache_key] = float(max(0.0, score))
            return self.cache[cache_key]
            
            # Check if scaler is fitted and we have enough training data
            if not self.audio_scaler_fitted or len(self.training_data['audio']['features']) < 10:
                # Not enough training data or scaler not fitted, use heuristic
                return 0.0
            
            # Check for feature count mismatch
            if self.expected_audio_features is not None and len(feature_vector) != self.expected_audio_features:
                logger.warning(f"Audio feature mismatch: got {len(feature_vector)}, expected {self.expected_audio_features}. Resetting model.")
                self._reset_audio_model()
                return 0.0
            
            scaled = self.audio_scaler.transform([feature_vector])
            score = self.audio_model.predict(scaled)[0]
            return float(max(0.0, score))
        except Exception as e:
            logger.error(f"Audio prediction failed: {e}")
            return 0.0
    
    def predict_video_score(self, features: Dict) -> float:
        """Predict highlight score for video features with caching"""
        try:
            # Generar clave de cache basada en características
            cache_key = hash(str(sorted(features.items())))
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            feature_vector = self._dict_to_vector(features)
            
            # Check if scaler is fitted and we have enough training data
            if not self.video_scaler_fitted or len(self.training_data['video']['features']) < 10:
                return 0.0
            
            # Check for feature count mismatch
            if self.expected_video_features is not None and len(feature_vector) != self.expected_video_features:
                logger.warning(f"Video feature mismatch: got {len(feature_vector)}, expected {self.expected_video_features}. Resetting model.")
                self._reset_video_model()
                return 0.0
            
            scaled = self.video_scaler.transform([feature_vector])
            score = self.video_model.predict(scaled)[0]
            return float(max(0.0, score))
        except Exception as e:
            logger.error(f"Video prediction failed: {e}")
            return 0.0
    
    def add_training_sample(self, features: Dict, score: float, feature_type: str):
        """Add a training sample for continuous learning"""
        feature_vector = self._dict_to_vector(features)
        self.training_data[feature_type]['features'].append(feature_vector)
        self.training_data[feature_type]['scores'].append(score)
    
    def retrain(self):
        """Retrain models with accumulated data"""
        try:
            # Train audio model
            if len(self.training_data['audio']['features']) >= 10:
                X = np.array(self.training_data['audio']['features'])
                y = np.array(self.training_data['audio']['scores'])
                
                # Store expected feature count
                self.expected_audio_features = X.shape[1]
                
                self.audio_scaler.fit(X)
                X_scaled = self.audio_scaler.transform(X)
                self.audio_model.fit(X_scaled, y)
                self.audio_scaler_fitted = True
                logger.info(f"Retrained audio model with {len(X)} samples ({self.expected_audio_features} features)")
            
            # Train video model
            if len(self.training_data['video']['features']) >= 10:
                X = np.array(self.training_data['video']['features'])
                y = np.array(self.training_data['video']['scores'])
                
                # Store expected feature count
                self.expected_video_features = X.shape[1]
                
                self.video_scaler.fit(X)
                X_scaled = self.video_scaler.transform(X)
                self.video_model.fit(X_scaled, y)
                self.video_scaler_fitted = True
                logger.info(f"Retrained video model with {len(X)} samples ({self.expected_video_features} features)")
            
            self.save_model()
        except Exception as e:
            logger.error(f"Retraining failed: {e}")
    
    def _reset_audio_model(self):
        """Reset audio model when feature mismatch detected"""
        self.audio_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)
        self.audio_scaler = StandardScaler()
        self.audio_scaler_fitted = False
        self.training_data['audio'] = {'features': [], 'scores': []}
        self.expected_audio_features = None
        logger.info("Reset audio model due to feature mismatch")
    
    def _reset_video_model(self):
        """Reset video model when feature mismatch detected"""
        self.video_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)
        self.video_scaler = StandardScaler()
        self.video_scaler_fitted = False
        self.training_data['video'] = {'features': [], 'scores': []}
        self.expected_video_features = None
        logger.info("Reset video model due to feature mismatch")
    
    def _dict_to_vector(self, features: Dict) -> List[float]:
        """Convert feature dictionary to vector"""
        return [float(v) for v in features.values()]


class KickClipGenerator:
    """Main class orchestrating the clip generation pipeline"""
    
    def __init__(self, clip_duration=30, min_gap=10):
        self.processor = StreamProcessor()
        self.audio_analyzer = AudioAnalyzer()
        self.video_analyzer = VideoAnalyzer()
        self.ml_model = MLHighlightModel()
        
        self.clip_duration = clip_duration
        self.min_gap = min_gap  # Minimum gap between highlights
        
        # Base output directory
        self.base_output_dir = Path("output_clips")
        self.base_output_dir.mkdir(exist_ok=True)
        self.current_output_dir = None
        self.current_video_id = None
        
        # Clear any existing highlights
        self.audio_highlights = []
        self.video_highlights = []
    
    def process_stream(self, stream_url: str, progress_callback=None, max_audio_clips=25, max_video_clips=25, start_minute=None, end_minute=None) -> Tuple[List[Highlight], List[Highlight]]:
        """Process stream and detect highlights
        
        Args:
            stream_url: URL of the stream to process
            progress_callback: Optional callback for progress updates
            max_audio_clips: Maximum number of audio clips to return (default: 25, max: 25)
            max_video_clips: Maximum number of video clips to return (default: 25, max: 25)
            start_minute: Start time in minutes (None = from beginning)
            end_minute: End time in minutes (None = until end)
        """
        # Clear previous highlights
        self.audio_highlights = []
        self.video_highlights = []
        
        # Generate a unique ID for this video based on current timestamp and URL hash
        import hashlib
        video_id = f"{int(time.time())}_{hashlib.md5(stream_url.encode()).hexdigest()[:8]}"
        self.current_video_id = video_id
        self.current_output_dir = self.base_output_dir / video_id
        self.current_output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Processing video with ID: {video_id}")
        
        # Enforce maximum limits
        max_audio_clips = min(max_audio_clips, config.MAX_CLIPS_PER_TYPE)
        max_video_clips = min(max_video_clips, config.MAX_CLIPS_PER_TYPE)
        
        try:
            for chunk_info in self.processor.process_stream_chunks(stream_url, progress_callback, start_minute, end_minute):
                chunk_path = chunk_info['path']
                start_time = chunk_info['start_time']
                
                logger.info(f"Processing chunk {chunk_info['index']} at {start_time:.1f}s")
                
                # Extract features in paralelo
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=2) as executor:
                    audio_future = executor.submit(self.audio_analyzer.extract_audio_features, chunk_path)
                    video_future = executor.submit(self.video_analyzer.extract_video_features, chunk_path)
                    
                    audio_features = audio_future.result()
                    video_features = video_future.result()
                
                # Calculate scores
                if audio_features:
                    audio_score = self.audio_analyzer.detect_audio_highlights(audio_features)
                    ml_audio_score = self.ml_model.predict_audio_score(audio_features)
                    
                    # Combine heuristic and ML scores
                    combined_audio_score = (audio_score * 0.6 + ml_audio_score * 0.4) if ml_audio_score > 0 else audio_score
                    
                    highlight = Highlight(
                        start_time=start_time,
                        end_time=start_time + self.processor.chunk_duration,
                        score=combined_audio_score,
                        type='audio',
                        features=audio_features,
                        timestamp=datetime.now().isoformat()
                    )
                    self.audio_highlights.append(highlight)
                    
                    # Add to training data
                    self.ml_model.add_training_sample(audio_features, combined_audio_score, 'audio')
                
                if video_features:
                    video_score = self.video_analyzer.detect_video_highlights(video_features)
                    ml_video_score = self.ml_model.predict_video_score(video_features)
                    
                    combined_video_score = (video_score * 0.6 + ml_video_score * 0.4) if ml_video_score > 0 else video_score
                    
                    highlight = Highlight(
                        start_time=start_time,
                        end_time=start_time + self.processor.chunk_duration,
                        score=combined_video_score,
                        type='video',
                        features=video_features,
                        timestamp=datetime.now().isoformat()
                    )
                    self.video_highlights.append(highlight)
                    
                    self.ml_model.add_training_sample(video_features, combined_video_score, 'video')
                
                # Cleanup chunk
                try:
                    os.remove(chunk_path)
                except:
                    pass
            
            # Filter and rank highlights with user-specified limits
            self.audio_highlights = self._filter_highlights(self.audio_highlights, top_n=10, max_clips=max_audio_clips)
            self.video_highlights = self._filter_highlights(self.video_highlights, top_n=10, max_clips=max_video_clips)
            
            logger.info(f"Filtered to {len(self.audio_highlights)} audio and {len(self.video_highlights)} video highlights")
            
            # Retrain ML model with new data
            self.ml_model.retrain()
            
            return self.audio_highlights, self.video_highlights
            
        except Exception as e:
            logger.error(f"Stream processing failed: {e}")
            return [], []
        finally:
            self.processor.cleanup()
    
    def _filter_highlights(self, highlights: List[Highlight], top_n=10, max_clips=None) -> List[Highlight]:
        """Filter overlapping highlights and return top N"""
        if not highlights:
            return []
        
        # Apply max_clips limit if specified (overrides top_n)
        if max_clips is not None:
            top_n = min(top_n, max_clips)
        
        # Sort by score
        sorted_highlights = sorted(highlights, key=lambda x: x.score, reverse=True)
        
        # Remove overlapping highlights
        filtered = []
        for highlight in sorted_highlights:
            # Check if it overlaps with already selected highlights
            overlap = False
            for selected in filtered:
                if abs(highlight.start_time - selected.start_time) < self.min_gap:
                    overlap = True
                    break
            
            if not overlap:
                filtered.append(highlight)
            
            if len(filtered) >= top_n:
                break
        
        return sorted(filtered, key=lambda x: x.start_time)
    
    def generate_clips(self, stream_url: str, highlights: List[Highlight], prefix='clip') -> List[str]:
        """Generate video clips from highlights"""
        if not self.current_output_dir:
            self.current_output_dir = self.base_output_dir / f"{int(time.time())}"
            self.current_output_dir.mkdir(exist_ok=True)
            
        clip_paths = []
        
        for idx, highlight in enumerate(highlights):
            try:
                # Create a more descriptive filename with timestamp and score
                timestamp = int(highlight.start_time)
                minutes = timestamp // 60
                seconds = timestamp % 60
                score = int(highlight.score * 100)  # Convert to percentage
                
                output_filename = f"{prefix}_{idx+1:03d}_{minutes:02d}m{seconds:02d}s_{score:03d}_{highlight.type}.mp4"
                output_path = self.current_output_dir / output_filename
                
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract clip
                stream = ffmpeg.input(stream_url, ss=highlight.start_time, t=self.clip_duration)
                stream = ffmpeg.output(stream, str(output_path),
                                     codec='copy',
                                     loglevel='error')
                ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
                
                clip_paths.append(str(output_path))
                logger.info(f"Generated clip: {output_path}")
                
            except Exception as e:
                logger.error(f"Failed to generate clip {idx}: {e}")
                logger.exception("Clip generation error details:")
        
        return clip_paths
    
    def export_highlights_json(self, audio_highlights: List[Highlight], video_highlights: List[Highlight], output_path=None):
        """Export highlights to JSON"""
        if not output_path:
            if not self.current_output_dir:
                self.current_output_dir = self.base_output_dir / f"{int(time.time())}"
                self.current_output_dir.mkdir(exist_ok=True)
            output_path = self.current_output_dir / "highlights.json"
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'video_id': str(self.current_video_id) if hasattr(self, 'current_video_id') else 'unknown',
            'audio_highlights': [h.to_dict() for h in audio_highlights],
            'video_highlights': [h.to_dict() for h in video_highlights],
            'generated_at': datetime.now().isoformat(),
            'clip_duration': self.clip_duration,
            'min_gap': self.min_gap
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported highlights to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to export highlights: {e}")
            return None


if __name__ == "__main__":
    # Test with a stream URL
    generator = KickClipGenerator()
    
    # Example usage
    stream_url = "https://example.com/stream.m3u8"
    audio_highlights, video_highlights = generator.process_stream(stream_url)
    
    print(f"Found {len(audio_highlights)} audio highlights")
    print(f"Found {len(video_highlights)} video highlights")
    
    # Generate clips
    clips = generator.generate_clips(stream_url, audio_highlights + video_highlights)
    print(f"Generated {len(clips)} clips")
    
    # Export results
    generator.export_highlights_json(audio_highlights, video_highlights)
