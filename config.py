"""
Configuration file for Kick Clip Generator
Adjust these settings to optimize performance for your use case
"""

# Stream Processing Settings
CHUNK_DURATION = 30  # seconds - duration of each processing chunk
CHUNK_OVERLAP = 5    # seconds - overlap between chunks to avoid missing highlights
FRAME_SKIP = 5       # process every Nth frame for performance
MAX_STREAM_DURATION = 36000  # seconds (10 hours) - maximum stream duration to process

# Highlight Detection Settings
DEFAULT_CLIP_DURATION = 30  # seconds - default duration for generated clips
MIN_GAP_BETWEEN_HIGHLIGHTS = 10  # seconds - minimum time between highlights
TOP_N_HIGHLIGHTS = 10  # number of top highlights to return per type
MAX_CLIPS_PER_TYPE = 25  # maximum clips per type (audio/video) - prevents memory issues
MAX_TOTAL_CLIPS = 50  # maximum total clips to generate - hard limit for safety

# Audio Analysis Settings
AUDIO_SAMPLE_RATE = 22050  # Hz - sample rate for audio analysis
AUDIO_WEIGHT = 0.6  # weight for heuristic score in combined score
ML_AUDIO_WEIGHT = 0.4  # weight for ML score in combined score

# Video Analysis Settings
VIDEO_WEIGHT = 0.6  # weight for heuristic score in combined score
ML_VIDEO_WEIGHT = 0.4  # weight for ML score in combined score

# ML Model Settings
ML_MODEL_PATH = 'models/highlight_model.pkl'
MIN_TRAINING_SAMPLES = 10  # minimum samples before ML model is used
N_ESTIMATORS = 100  # number of trees in gradient boosting
LEARNING_RATE = 0.1  # learning rate for gradient boosting

# Network Settings
MAX_RETRIES = 5  # maximum number of retry attempts for failed requests
BACKOFF_FACTOR = 2  # exponential backoff factor for retries
REQUEST_TIMEOUT = 30  # seconds - timeout for HTTP requests

# User Agents for rotation (helps avoid 403 errors)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
]

# Directory Settings
TEMP_DIR = 'temp_chunks'
OUTPUT_DIR = 'output_clips'
MODEL_DIR = 'models'

# Gradio Interface Settings
GRADIO_SERVER_NAME = '0.0.0.0'
GRADIO_SERVER_PORT = 7860
GRADIO_SHARE = False  # set to True to create public link

# Logging Settings
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Performance Settings
ENABLE_GPU = False  # set to True if you have CUDA-capable GPU
MAX_WORKERS = 4  # maximum number of parallel workers for processing

# Feature Extraction Settings
# Audio features
EXTRACT_MFCC = True
N_MFCC = 13
EXTRACT_SPECTRAL = True
EXTRACT_TEMPO = True

# Video features
EXTRACT_MOTION = True
EXTRACT_EDGES = True
EXTRACT_COLOR = True

# Score Thresholds (for filtering low-quality highlights)
MIN_AUDIO_SCORE = 0.0  # minimum score for audio highlights
MIN_VIDEO_SCORE = 0.0  # minimum score for video highlights

# Advanced Settings
ENABLE_CONTINUOUS_LEARNING = True  # automatically retrain ML model
AUTO_SAVE_MODEL = True  # save model after each processing session
EXPORT_FEATURES = True  # export feature data for analysis
