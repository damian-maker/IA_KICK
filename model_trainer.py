"""
Model Trainer - Integrates user ratings into ML model training
Uses feedback from rated clips to improve highlight detection
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import pickle
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from clip_manager import ClipManager

logger = logging.getLogger(__name__)


class RatingBasedTrainer:
    """Trains ML models using user ratings as ground truth"""
    
    def __init__(self, clip_manager: ClipManager, model_path: str = "models/highlight_model.pkl"):
        self.clip_manager = clip_manager
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(exist_ok=True)
    
    def prepare_training_data(self) -> Tuple[Dict, Dict]:
        """Prepare training data from rated clips"""
        features_list, ratings_list = self.clip_manager.get_training_data()
        
        if not features_list:
            logger.warning("No rated clips available for training")
            return {'audio': {'X': [], 'y': []}, 'video': {'X': [], 'y': []}}
        
        # Separate by clip type
        audio_features = []
        audio_ratings = []
        video_features = []
        video_ratings = []
        
        for features, rating in zip(features_list, ratings_list):
            # Normalize rating to 0-1 scale (from 1-5 stars)
            normalized_rating = (rating - 1) / 4.0
            
            # Extract feature vector
            feature_vector = self._extract_feature_vector(features)
            
            # Determine type based on features present
            if self._is_audio_features(features):
                audio_features.append(feature_vector)
                audio_ratings.append(normalized_rating)
            else:
                video_features.append(feature_vector)
                video_ratings.append(normalized_rating)
        
        logger.info(f"Prepared {len(audio_features)} audio and {len(video_features)} video training samples")
        
        return {
            'audio': {
                'X': np.array(audio_features) if audio_features else np.array([]),
                'y': np.array(audio_ratings) if audio_ratings else np.array([])
            },
            'video': {
                'X': np.array(video_features) if video_features else np.array([]),
                'y': np.array(video_ratings) if video_ratings else np.array([])
            }
        }
    
    def train_from_ratings(self, min_samples: int = 10) -> bool:
        """Train or update models using rated clips"""
        try:
            # Get training data
            training_data = self.prepare_training_data()
            
            # Load existing model or create new one
            model_data = self._load_or_create_model()
            
            trained = False
            
            # Train audio model
            if len(training_data['audio']['X']) >= min_samples:
                logger.info(f"Training audio model with {len(training_data['audio']['X'])} samples")
                
                audio_scaler = StandardScaler()
                X_scaled = audio_scaler.fit_transform(training_data['audio']['X'])
                
                audio_model = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42
                )
                audio_model.fit(X_scaled, training_data['audio']['y'])
                
                model_data['audio_model'] = audio_model
                model_data['audio_scaler'] = audio_scaler
                
                # Update training data
                model_data['training_data']['audio']['features'] = training_data['audio']['X'].tolist()
                model_data['training_data']['audio']['scores'] = training_data['audio']['y'].tolist()
                
                # Store feature count for validation
                model_data['audio_feature_count'] = training_data['audio']['X'].shape[1]
                
                trained = True
                logger.info("Audio model training complete")
            else:
                logger.info(f"Not enough audio samples ({len(training_data['audio']['X'])}/{min_samples})")
            
            # Train video model
            if len(training_data['video']['X']) >= min_samples:
                logger.info(f"Training video model with {len(training_data['video']['X'])} samples")
                
                video_scaler = StandardScaler()
                X_scaled = video_scaler.fit_transform(training_data['video']['X'])
                
                video_model = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42
                )
                video_model.fit(X_scaled, training_data['video']['y'])
                
                model_data['video_model'] = video_model
                model_data['video_scaler'] = video_scaler
                
                # Update training data
                model_data['training_data']['video']['features'] = training_data['video']['X'].tolist()
                model_data['training_data']['video']['scores'] = training_data['video']['y'].tolist()
                
                # Store feature count for validation
                model_data['video_feature_count'] = training_data['video']['X'].shape[1]
                
                trained = True
                logger.info("Video model training complete")
            else:
                logger.info(f"Not enough video samples ({len(training_data['video']['X'])}/{min_samples})")
            
            # Save updated model
            if trained:
                self._save_model(model_data)
                logger.info(f"Model saved to {self.model_path}")
                return True
            else:
                logger.warning("No models were trained due to insufficient data")
                return False
                
        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            return False
    
    def _load_or_create_model(self) -> Dict:
        """Load existing model or create new structure"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                logger.info("Loaded existing model")
                return data
        except Exception as e:
            logger.warning(f"Could not load existing model: {e}")
        
        # Create new model structure
        return {
            'audio_model': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1),
            'video_model': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1),
            'audio_scaler': StandardScaler(),
            'video_scaler': StandardScaler(),
            'training_data': {
                'audio': {'features': [], 'scores': []},
                'video': {'features': [], 'scores': []}
            },
            'audio_feature_count': None,
            'video_feature_count': None
        }
    
    def _save_model(self, model_data: Dict):
        """Save model to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def _extract_feature_vector(self, features: Dict) -> List[float]:
        """Extract feature vector from feature dictionary"""
        # Define expected feature keys in order
        feature_keys = [
            'rms_mean', 'rms_std', 'zcr_mean', 'zcr_std',
            'spectral_centroid_mean', 'spectral_centroid_std',
            'spectral_rolloff_mean', 'spectral_rolloff_std',
            'tempo', 'beat_strength',
            'motion_mean', 'motion_std', 'edge_density',
            'color_variance', 'brightness_mean'
        ]
        
        # Extract values, use 0.0 if key doesn't exist
        vector = []
        for key in feature_keys:
            vector.append(float(features.get(key, 0.0)))
        
        return vector
    
    def _is_audio_features(self, features: Dict) -> bool:
        """Determine if features are audio-based"""
        audio_keys = ['rms_mean', 'zcr_mean', 'spectral_centroid_mean', 'tempo']
        return any(key in features for key in audio_keys)
    
    def get_training_progress(self) -> Dict:
        """Get information about training progress"""
        stats = self.clip_manager.get_statistics()
        
        # Check if model exists and is trained
        model_trained = self.model_path.exists()
        
        if model_trained:
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                audio_samples = len(data['training_data']['audio']['features'])
                video_samples = len(data['training_data']['video']['features'])
            except:
                audio_samples = 0
                video_samples = 0
        else:
            audio_samples = 0
            video_samples = 0
        
        return {
            'total_clips': stats['total_clips'],
            'rated_clips': stats['rated_clips'],
            'unrated_clips': stats['total_clips'] - stats['rated_clips'],
            'model_trained': model_trained,
            'audio_training_samples': audio_samples,
            'video_training_samples': video_samples,
            'ready_for_training': stats['rated_clips'] >= 10
        }


def auto_train_if_ready(clip_manager: ClipManager, min_samples: int = 10) -> bool:
    """Automatically train model if enough rated clips are available"""
    trainer = RatingBasedTrainer(clip_manager)
    progress = trainer.get_training_progress()
    
    if progress['ready_for_training'] and progress['rated_clips'] % 5 == 0:
        # Retrain every 5 new ratings
        logger.info("Auto-training triggered")
        return trainer.train_from_ratings(min_samples)
    
    return False


if __name__ == "__main__":
    # Test the trainer
    logging.basicConfig(level=logging.INFO)
    
    manager = ClipManager()
    trainer = RatingBasedTrainer(manager)
    
    progress = trainer.get_training_progress()
    print(f"Training Progress: {progress}")
    
    if progress['ready_for_training']:
        print("Training model...")
        success = trainer.train_from_ratings()
        print(f"Training {'successful' if success else 'failed'}")
    else:
        print(f"Need {10 - progress['rated_clips']} more rated clips to train")
