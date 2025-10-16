"""
Clip Manager - Handles clip storage, ratings, and database operations
Enables continuous learning by tracking user feedback on generated clips
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import shutil

logger = logging.getLogger(__name__)


@dataclass
class ClipRecord:
    """Represents a clip record in the database"""
    id: Optional[int]
    filename: str
    filepath: str
    start_time: float
    end_time: float
    duration: float
    score: float
    clip_type: str  # 'audio' or 'video'
    features: str  # JSON string of features
    rating: Optional[int]  # 1-5 stars, None if not rated
    created_at: str
    rated_at: Optional[str]
    source_url: Optional[str]
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'filepath': self.filepath,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'score': self.score,
            'clip_type': self.clip_type,
            'features': json.loads(self.features) if isinstance(self.features, str) else self.features,
            'rating': self.rating,
            'created_at': self.created_at,
            'rated_at': self.rated_at,
            'source_url': self.source_url
        }


class ClipDatabase:
    """SQLite database for managing clips and ratings"""
    
    def __init__(self, db_path: str = "clips.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create clips table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                duration REAL NOT NULL,
                score REAL NOT NULL,
                clip_type TEXT NOT NULL,
                features TEXT NOT NULL,
                rating INTEGER,
                created_at TEXT NOT NULL,
                rated_at TEXT,
                source_url TEXT,
                UNIQUE(filepath)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rating ON clips(rating)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_clip_type ON clips(clip_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON clips(created_at)
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_clip(self, clip: ClipRecord) -> int:
        """Add a new clip to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO clips (filename, filepath, start_time, end_time, duration, 
                                 score, clip_type, features, rating, created_at, rated_at, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                clip.filename, clip.filepath, clip.start_time, clip.end_time,
                clip.duration, clip.score, clip.clip_type, clip.features,
                clip.rating, clip.created_at, clip.rated_at, clip.source_url
            ))
            conn.commit()
            clip_id = cursor.lastrowid
            logger.info(f"Added clip {clip.filename} to database (ID: {clip_id})")
            return clip_id
        except sqlite3.IntegrityError:
            logger.warning(f"Clip {clip.filename} already exists in database")
            # Return existing ID
            cursor.execute("SELECT id FROM clips WHERE filepath = ?", (clip.filepath,))
            result = cursor.fetchone()
            return result[0] if result else -1
        finally:
            conn.close()
    
    def update_rating(self, clip_id: int, rating: int) -> bool:
        """Update the rating for a clip"""
        if not 1 <= rating <= 5:
            logger.error(f"Invalid rating: {rating}. Must be between 1 and 5")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE clips 
                SET rating = ?, rated_at = ?
                WHERE id = ?
            """, (rating, datetime.now().isoformat(), clip_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Updated rating for clip ID {clip_id} to {rating}")
                return True
            else:
                logger.warning(f"Clip ID {clip_id} not found")
                return False
        finally:
            conn.close()
    
    def get_clip(self, clip_id: int) -> Optional[ClipRecord]:
        """Get a clip by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM clips WHERE id = ?", (clip_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ClipRecord(*row)
        return None
    
    def get_all_clips(self, limit: Optional[int] = None, 
                     clip_type: Optional[str] = None,
                     rated_only: bool = False) -> List[ClipRecord]:
        """Get all clips with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM clips WHERE 1=1"
        params = []
        
        if clip_type:
            query += " AND clip_type = ?"
            params.append(clip_type)
        
        if rated_only:
            query += " AND rating IS NOT NULL"
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [ClipRecord(*row) for row in rows]
    
    def get_rated_clips(self) -> List[ClipRecord]:
        """Get all clips that have been rated"""
        return self.get_all_clips(rated_only=True)
    
    def get_training_data(self) -> Tuple[List[Dict], List[int]]:
        """Get features and ratings for ML training"""
        rated_clips = self.get_rated_clips()
        
        features = []
        ratings = []
        
        for clip in rated_clips:
            try:
                feature_dict = json.loads(clip.features)
                features.append(feature_dict)
                ratings.append(clip.rating)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse features for clip {clip.id}")
                continue
        
        logger.info(f"Retrieved {len(features)} training samples from database")
        return features, ratings
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total clips
        cursor.execute("SELECT COUNT(*) FROM clips")
        stats['total_clips'] = cursor.fetchone()[0]
        
        # Rated clips
        cursor.execute("SELECT COUNT(*) FROM clips WHERE rating IS NOT NULL")
        stats['rated_clips'] = cursor.fetchone()[0]
        
        # Average rating
        cursor.execute("SELECT AVG(rating) FROM clips WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()[0]
        stats['average_rating'] = round(avg_rating, 2) if avg_rating else 0
        
        # Rating distribution
        cursor.execute("""
            SELECT rating, COUNT(*) 
            FROM clips 
            WHERE rating IS NOT NULL 
            GROUP BY rating 
            ORDER BY rating
        """)
        stats['rating_distribution'] = dict(cursor.fetchall())
        
        # Clips by type
        cursor.execute("""
            SELECT clip_type, COUNT(*) 
            FROM clips 
            GROUP BY clip_type
        """)
        stats['clips_by_type'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    def delete_clip(self, clip_id: int, delete_file: bool = False) -> bool:
        """Delete a clip from database and optionally from filesystem"""
        clip = self.get_clip(clip_id)
        if not clip:
            logger.warning(f"Clip ID {clip_id} not found")
            return False
        
        # Delete file if requested
        if delete_file:
            try:
                Path(clip.filepath).unlink(missing_ok=True)
                logger.info(f"Deleted file: {clip.filepath}")
            except Exception as e:
                logger.error(f"Could not delete file {clip.filepath}: {e}")
        
        # Delete from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted clip ID {clip_id} from database")
        return True


class ClipManager:
    """High-level clip management interface"""
    
    def __init__(self, output_dir: str = "output_clips", db_path: str = "clips.db"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.db = ClipDatabase(db_path)
    
    def register_clip(self, filepath: str, start_time: float, end_time: float,
                     score: float, clip_type: str, features: Dict,
                     source_url: Optional[str] = None) -> int:
        """Register a newly generated clip in the database"""
        filepath = Path(filepath)
        
        clip = ClipRecord(
            id=None,
            filename=filepath.name,
            filepath=str(filepath.absolute()),
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            score=score,
            clip_type=clip_type,
            features=json.dumps(features),
            rating=None,
            created_at=datetime.now().isoformat(),
            rated_at=None,
            source_url=source_url
        )
        
        return self.db.add_clip(clip)
    
    def rate_clip(self, clip_id: int, rating: int) -> bool:
        """Rate a clip (1-5 stars)"""
        return self.db.update_rating(clip_id, rating)
    
    def get_clips_for_review(self, limit: int = 20) -> List[ClipRecord]:
        """Get unrated clips for review"""
        all_clips = self.db.get_all_clips(limit=limit * 2)  # Get more to filter
        unrated = [clip for clip in all_clips if clip.rating is None]
        return unrated[:limit]
    
    def get_clip_gallery(self, limit: int = 50) -> List[Dict]:
        """Get clips formatted for gallery display"""
        clips = self.db.get_all_clips(limit=limit)
        return [clip.to_dict() for clip in clips]
    
    def export_clip(self, clip_id: int, destination: str) -> bool:
        """Export/copy a clip to a destination"""
        clip = self.db.get_clip(clip_id)
        if not clip:
            return False
        
        try:
            shutil.copy2(clip.filepath, destination)
            logger.info(f"Exported clip {clip.filename} to {destination}")
            return True
        except Exception as e:
            logger.error(f"Could not export clip: {e}")
            return False
    
    def get_training_data(self) -> Tuple[List[Dict], List[int]]:
        """Get training data for ML model improvement"""
        return self.db.get_training_data()
    
    def get_statistics(self) -> Dict:
        """Get clip statistics"""
        return self.db.get_statistics()
    
    def cleanup_missing_files(self) -> int:
        """Remove database entries for clips that no longer exist"""
        clips = self.db.get_all_clips()
        removed = 0
        
        for clip in clips:
            if not Path(clip.filepath).exists():
                self.db.delete_clip(clip.id, delete_file=False)
                removed += 1
        
        logger.info(f"Cleaned up {removed} missing clip entries")
        return removed


if __name__ == "__main__":
    # Test the clip manager
    logging.basicConfig(level=logging.INFO)
    
    manager = ClipManager()
    stats = manager.get_statistics()
    print(f"Database Statistics: {json.dumps(stats, indent=2)}")
