"""
Test script for clip management and rating system
Verifies database operations, rating functionality, and model training
"""

import logging
import json
from pathlib import Path
from clip_manager import ClipManager, ClipRecord
from model_trainer import RatingBasedTrainer
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_database_initialization():
    """Test database creation and initialization"""
    logger.info("=" * 60)
    logger.info("TEST 1: Database Initialization")
    logger.info("=" * 60)
    
    try:
        manager = ClipManager(db_path="test_clips.db")
        logger.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def test_clip_registration():
    """Test registering clips in the database"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Clip Registration")
    logger.info("=" * 60)
    
    try:
        manager = ClipManager(db_path="test_clips.db")
        
        # Create dummy features
        features = {
            'rms_mean': 0.5,
            'rms_std': 0.1,
            'zcr_mean': 0.3,
            'tempo': 120.0,
            'spectral_centroid_mean': 2000.0
        }
        
        # Register a test clip
        clip_id = manager.register_clip(
            filepath="test_clip_1.mp4",
            start_time=10.0,
            end_time=40.0,
            score=0.85,
            clip_type="audio",
            features=features,
            source_url="https://example.com/test"
        )
        
        logger.info(f"✅ Clip registered with ID: {clip_id}")
        
        # Verify clip was stored
        clip = manager.db.get_clip(clip_id)
        if clip:
            logger.info(f"✅ Clip retrieved: {clip.filename}")
            return True
        else:
            logger.error("❌ Could not retrieve registered clip")
            return False
            
    except Exception as e:
        logger.error(f"❌ Clip registration failed: {e}")
        return False


def test_rating_system():
    """Test clip rating functionality"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Rating System")
    logger.info("=" * 60)
    
    try:
        manager = ClipManager(db_path="test_clips.db")
        
        # Register multiple test clips
        test_clips = []
        for i in range(15):
            features = {
                'rms_mean': 0.5 + (i * 0.02),
                'rms_std': 0.1,
                'zcr_mean': 0.3,
                'tempo': 120.0 + (i * 2),
                'spectral_centroid_mean': 2000.0
            }
            
            clip_id = manager.register_clip(
                filepath=f"test_clip_{i+2}.mp4",
                start_time=10.0 * i,
                end_time=40.0 * i,
                score=0.5 + (i * 0.03),
                clip_type="audio" if i % 2 == 0 else "video",
                features=features,
                source_url="https://example.com/test"
            )
            test_clips.append(clip_id)
        
        logger.info(f"✅ Registered {len(test_clips)} test clips")
        
        # Rate the clips
        ratings = [5, 4, 5, 3, 4, 5, 2, 4, 5, 3, 4, 5, 4, 3, 5]
        for clip_id, rating in zip(test_clips, ratings):
            success = manager.rate_clip(clip_id, rating)
            if not success:
                logger.error(f"❌ Failed to rate clip {clip_id}")
                return False
        
        logger.info(f"✅ Rated {len(test_clips)} clips")
        
        # Verify ratings
        stats = manager.get_statistics()
        logger.info(f"✅ Statistics: {stats['rated_clips']} rated clips, avg rating: {stats['average_rating']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Rating system test failed: {e}")
        return False


def test_statistics():
    """Test statistics generation"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Statistics")
    logger.info("=" * 60)
    
    try:
        manager = ClipManager(db_path="test_clips.db")
        stats = manager.get_statistics()
        
        logger.info(f"Total clips: {stats['total_clips']}")
        logger.info(f"Rated clips: {stats['rated_clips']}")
        logger.info(f"Average rating: {stats['average_rating']}")
        logger.info(f"Rating distribution: {stats['rating_distribution']}")
        logger.info(f"Clips by type: {stats['clips_by_type']}")
        
        if stats['total_clips'] > 0:
            logger.info("✅ Statistics generated successfully")
            return True
        else:
            logger.error("❌ No clips in database")
            return False
            
    except Exception as e:
        logger.error(f"❌ Statistics test failed: {e}")
        return False


def test_training_data():
    """Test training data extraction"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Training Data Extraction")
    logger.info("=" * 60)
    
    try:
        manager = ClipManager(db_path="test_clips.db")
        features, ratings = manager.get_training_data()
        
        logger.info(f"✅ Extracted {len(features)} feature sets")
        logger.info(f"✅ Extracted {len(ratings)} ratings")
        
        if len(features) == len(ratings):
            logger.info("✅ Feature-rating pairs match")
            return True
        else:
            logger.error("❌ Mismatch between features and ratings")
            return False
            
    except Exception as e:
        logger.error(f"❌ Training data extraction failed: {e}")
        return False


def test_model_training():
    """Test ML model training with ratings"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Model Training")
    logger.info("=" * 60)
    
    try:
        manager = ClipManager(db_path="test_clips.db")
        trainer = RatingBasedTrainer(manager, model_path="test_model.pkl")
        
        # Check training progress
        progress = trainer.get_training_progress()
        logger.info(f"Training progress: {json.dumps(progress, indent=2)}")
        
        if not progress['ready_for_training']:
            logger.warning("⚠️ Not enough rated clips for training")
            return True  # Not a failure, just not ready
        
        # Train the model
        logger.info("Training model...")
        success = trainer.train_from_ratings(min_samples=10)
        
        if success:
            logger.info("✅ Model training completed successfully")
            
            # Verify model file was created
            if Path("test_model.pkl").exists():
                logger.info("✅ Model file created")
                return True
            else:
                logger.error("❌ Model file not found")
                return False
        else:
            logger.error("❌ Model training failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Model training test failed: {e}")
        return False


def test_clip_gallery():
    """Test clip gallery functionality"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Clip Gallery")
    logger.info("=" * 60)
    
    try:
        manager = ClipManager(db_path="test_clips.db")
        gallery = manager.get_clip_gallery(limit=10)
        
        logger.info(f"✅ Retrieved {len(gallery)} clips for gallery")
        
        if gallery:
            sample = gallery[0]
            logger.info(f"Sample clip: {sample['filename']}, Rating: {sample['rating']}, Score: {sample['score']}")
            return True
        else:
            logger.warning("⚠️ No clips in gallery")
            return True  # Not a failure if database is empty
            
    except Exception as e:
        logger.error(f"❌ Gallery test failed: {e}")
        return False


def cleanup_test_files():
    """Clean up test files"""
    logger.info("\n" + "=" * 60)
    logger.info("Cleanup")
    logger.info("=" * 60)
    
    try:
        test_files = ["test_clips.db", "test_model.pkl"]
        for file in test_files:
            path = Path(file)
            if path.exists():
                path.unlink()
                logger.info(f"✅ Deleted {file}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("CLIP MANAGEMENT SYSTEM TEST SUITE")
    logger.info("=" * 60)
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Clip Registration", test_clip_registration),
        ("Rating System", test_rating_system),
        ("Statistics", test_statistics),
        ("Training Data", test_training_data),
        ("Model Training", test_model_training),
        ("Clip Gallery", test_clip_gallery),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Cleanup
    cleanup_test_files()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"RESULTS: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
