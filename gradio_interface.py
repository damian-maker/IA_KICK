"""
Gradio Interface for Kick Clip Generator
Beautiful, modern UI for generating highlight clips
"""

import gradio as gr
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from kick_clip_generator import KickClipGenerator, Highlight
from kick_api import KickAPI
from clip_manager import ClipManager
from model_trainer import RatingBasedTrainer, auto_train_if_ready
import config
import logging
import shutil

logger = logging.getLogger(__name__)


class GradioInterface:
    """Gradio interface wrapper for the clip generator"""
    
    def __init__(self):
        self.generator = KickClipGenerator()
        self.kick_api = KickAPI()
        self.clip_manager = ClipManager()
        self.model_trainer = RatingBasedTrainer(self.clip_manager)
        self.current_audio_highlights = []
        self.current_video_highlights = []
        self.processing = False
        self.temp_vod_file = None
        self.original_url = None
        self.current_clips = []  # Store generated clip info
    
    def process_stream_wrapper(self, stream_url, clip_duration, min_gap, max_audio_clips, max_video_clips, start_minute, end_minute, progress=gr.Progress()):
        """Wrapper for processing stream with progress updates"""
        if not stream_url:
            return "❌ Please provide a stream URL", None, None, None, None
        
        if self.processing:
            return "⚠️ Already processing a stream. Please wait.", None, None, None, None
        
        self.processing = True
        
        try:
            # Update generator settings
            self.generator.clip_duration = int(clip_duration)
            self.generator.min_gap = int(min_gap)
            
            # Enforce clip limits
            max_audio_clips = min(int(max_audio_clips), config.MAX_CLIPS_PER_TYPE)
            max_video_clips = min(int(max_video_clips), config.MAX_CLIPS_PER_TYPE)
            
            # Handle time range (convert to None if 0)
            start_min = start_minute if start_minute > 0 else None
            end_min = end_minute if end_minute > 0 else None
            
            # Store original URL for clip generation
            self.original_url = stream_url
            
            # Handle Kick VODs specially (they require download via yt-dlp)
            processed_url = stream_url
            
            if 'kick.com' in stream_url and not stream_url.endswith(('.m3u8', '.mp4')):
                # Check if it's a VOD URL
                video_id = self.kick_api.extract_video_id_from_url(stream_url)
                
                if video_id:
                    # It's a VOD - try to download it first using yt-dlp
                    progress(0, desc="Detected Kick VOD - downloading selected segment...")
                    logger.info("Detected Kick VOD - downloading via yt-dlp...")
                    self.temp_vod_file = Path(config.TEMP_DIR) / f"vod_{video_id}.mp4"
                    
                    # Convertir minutos a formato de tiempo para yt-dlp
                    start_time_str = None
                    end_time_str = None
                    
                    if start_min is not None:
                        start_time_str = str(int(start_min * 60))
                    if end_min is not None:
                        end_time_str = str(int(end_min * 60))
                    
                    if self.kick_api.download_vod_with_ytdlp(
                        stream_url, 
                        str(self.temp_vod_file),
                        start_time_str,
                        end_time_str
                    ):
                        processed_url = str(self.temp_vod_file)
                        logger.info(f"VOD segment downloaded, processing: {processed_url}")
                    else:
                        # Fallback: attempt to resolve a playable stream URL and proceed without full download
                        logger.warning("VOD download failed. Attempting fallback to resolved stream URL...")
                        resolved_url = self.kick_api.resolve_kick_url(stream_url)
                        if resolved_url:
                            processed_url = resolved_url
                            logger.info(f"Fallback succeeded. Proceeding with resolved URL: {processed_url}")
                        else:
                            return "❌ Could not download or resolve Kick VOD. Check logs for details.", None, None, None, None
                else:
                    # It's a live stream - resolve URL
                    progress(0, desc="Resolving Kick live stream URL...")
                    logger.info("Resolving Kick live stream URL...")
                    resolved_url = self.kick_api.resolve_kick_url(stream_url)
                    if resolved_url:
                        processed_url = resolved_url
                        logger.info(f"Resolved to: {processed_url}")
                    else:
                        return "❌ Could not resolve Kick URL. Make sure yt-dlp is installed.", None, None, None, None
            progress(0.1, desc="Starting stream analysis...")
            
            def progress_callback(chunk_idx, current_time, total_duration):
                # Reserve 0.1-0.9 for processing, 0.9-1.0 for final analysis
                pct = 0.1 + (min(current_time / total_duration, 1.0) * 0.8)
                chunks_left = int((total_duration - current_time) / self.generator.processor.chunk_duration)
                time_left = chunks_left * self.generator.processor.chunk_duration
                
                status = f"""
🔄 Procesando fragmento {chunk_idx}
⏱️ Tiempo actual: {int(current_time/60)}:{int(current_time%60):02d}
⌛ Tiempo restante estimado: {int(time_left/60)}:{int(time_left%60):02d}
📊 Progreso: {pct*100:.1f}%
"""
                progress(pct, desc=status)
            # Process stream with clip limits and time range
            audio_highlights, video_highlights = self.generator.process_stream(
                processed_url, 
                progress_callback=progress_callback,
                max_audio_clips=max_audio_clips,
                max_video_clips=max_video_clips,
                start_minute=start_min,
                end_minute=end_min
            )
            
            self.current_audio_highlights = audio_highlights
            self.current_video_highlights = video_highlights
            
            progress(1.0, desc="Analysis complete!")
            
            # Create summary
            summary = f"""
✅ **Analysis Complete!**

📊 **Results:**
- 🎵 Audio Highlights: {len(audio_highlights)}
- 🎬 Video Highlights: {len(video_highlights)}
- ⏱️ Total Highlights: {len(audio_highlights) + len(video_highlights)}

🎯 **Top Scores:**
- Best Audio: {max([h.score for h in audio_highlights], default=0):.2f}
- Best Video: {max([h.score for h in video_highlights], default=0):.2f}

💾 Ready to generate clips!
"""
            
            # Create dataframes for display
            audio_df = self._highlights_to_dataframe(audio_highlights, 'Audio')
            video_df = self._highlights_to_dataframe(video_highlights, 'Video')
            
            return summary, audio_df, video_df, gr.update(interactive=True), gr.update(interactive=True)
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return f"❌ Error: {str(e)}", None, None, None, None
        finally:
            self.processing = False
    
    def generate_clips_wrapper(self, stream_url, highlight_type, progress=gr.Progress()):
        """Generate clips from detected highlights"""
        if not stream_url:
            return "❌ Please provide a stream URL", None, gr.update()
        
        if not self.current_audio_highlights and not self.current_video_highlights:
            return "❌ No highlights detected. Please analyze a stream first.", None, gr.update()
        
        try:
            progress(0, desc="Generating clips...")
            
            if highlight_type == "Audio Only":
                highlights = self.current_audio_highlights
                prefix = "audio_highlight"
            elif highlight_type == "Video Only":
                highlights = self.current_video_highlights
                prefix = "video_highlight"
            else:  # Both
                highlights = self.current_audio_highlights + self.current_video_highlights
                prefix = "highlight"
            
            if not highlights:
                return f"❌ No {highlight_type.lower()} highlights available", None, gr.update()
            
            # Use the temp VOD file if it exists, otherwise use original URL
            source_url = str(self.temp_vod_file) if self.temp_vod_file and Path(self.temp_vod_file).exists() else stream_url
            
            # Generate clips and register in database
            clip_paths = []
            self.current_clips = []
            total_highlights = len(highlights)
            
            logger.info(f"Generating {total_highlights} clips...")
            progress(0.1, desc=f"Preparing to generate {total_highlights} clips...")
            
            for idx, highlight in enumerate(highlights):
                current_progress = 0.1 + (0.9 * (idx / total_highlights))
                progress(current_progress, desc=f"Generating clip {idx + 1}/{total_highlights}")
                
                try:
                    # Verificar que el tiempo del highlight está dentro del rango descargado
                    if self.temp_vod_file:
                        import ffmpeg
                        probe = ffmpeg.probe(str(self.temp_vod_file))
                        vod_duration = float(probe['format']['duration'])
                        if highlight.start_time > vod_duration:
                            logger.warning(f"Skip clip {idx+1}: start time {highlight.start_time}s exceeds VOD duration {vod_duration}s")
                            continue
                    
                    clips = self.generator.generate_clips(source_url, [highlight], prefix=f"{prefix}_{idx+1}")
                except Exception as e:
                    logger.error(f"Error generating clip {idx+1}: {e}")
                    continue
                    
                # Register each clip in the database
                for clip_path in clips:
                    clip_id = self.clip_manager.register_clip(
                        filepath=clip_path,
                        start_time=highlight.start_time,
                        end_time=highlight.end_time,
                        score=highlight.score,
                        clip_type=highlight.type,
                        features=highlight.features,
                        source_url=stream_url
                    )
                    self.current_clips.append({
                        'id': clip_id,
                        'path': clip_path,
                        'highlight': highlight
                    })
                
                clip_paths.extend(clips)
            
            # Export highlights JSON
            json_path = self.generator.output_dir / f"highlights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.generator.export_highlights_json(
                self.current_audio_highlights,
                self.current_video_highlights,
                str(json_path)
            )
            
            progress(1.0, desc="Clips generated!")
            
            result = f"""
✅ **Clips Generated Successfully!**

📁 **Output:**
- Generated {len(clip_paths)} clips
- Location: `{self.generator.output_dir}`
- Metadata: `{json_path.name}`
- Registered in database for rating

🎬 **Clips:**
"""
            for path in clip_paths:
                result += f"\n- {Path(path).name}"
            
            # Return first clip for preview
            preview_video = clip_paths[0] if clip_paths else None
            
            # Update gallery
            gallery_update = self._get_clip_gallery_update()
            
            return result, preview_video, gallery_update
            
        except Exception as e:
            logger.error(f"Clip generation failed: {e}")
            return f"❌ Error generating clips: {str(e)}", None, gr.update()
        finally:
            # Cleanup temporary VOD file after clip generation
            self._cleanup_temp_vod()
    
    def _cleanup_temp_vod(self):
        """Clean up temporary VOD file"""
        if self.temp_vod_file and Path(self.temp_vod_file).exists():
            try:
                Path(self.temp_vod_file).unlink()
                logger.info("Cleaned up temporary VOD file")
                self.temp_vod_file = None
            except Exception as e:
                logger.warning(f"Could not delete temp VOD file: {e}")
    
    def _highlights_to_dataframe(self, highlights, highlight_type):
        """Convert highlights to pandas dataframe for display"""
        if not highlights:
            return pd.DataFrame(columns=['Rank', 'Type', 'Start Time', 'Duration', 'Score'])
        
        data = []
        for idx, h in enumerate(highlights, 1):
            data.append({
                'Rank': idx,
                'Type': highlight_type,
                'Start Time': f"{int(h.start_time // 60)}:{int(h.start_time % 60):02d}",
                'Duration': f"{int((h.end_time - h.start_time))}s",
                'Score': f"{h.score:.2f}"
            })
        
        return pd.DataFrame(data)
    
    def _get_clip_gallery_update(self):
        """Get updated clip gallery data"""
        clips = self.clip_manager.get_clip_gallery(limit=50)
        if not clips:
            return []
        
        # Return list of (video_path, caption) tuples for gallery
        gallery_items = []
        for clip in clips:
            caption = f"⭐ {clip['rating'] if clip['rating'] else 'Not rated'} | Score: {clip['score']:.2f} | {clip['clip_type']}"
            gallery_items.append((clip['filepath'], caption))
        
        return gallery_items
    
    def load_clips_for_rating(self):
        """Load unrated clips for review"""
        clips = self.clip_manager.get_clips_for_review(limit=20)
        
        if not clips:
            return "✅ All clips have been rated!", None, gr.update(choices=[]), gr.update(interactive=False)
        
        # Create dropdown choices
        choices = [f"ID {clip.id}: {clip.filename}" for clip in clips]
        
        # Load first clip
        first_clip = clips[0]
        video_path = first_clip.filepath if Path(first_clip.filepath).exists() else None
        
        info = f"""
**Clip Information:**
- **File:** {first_clip.filename}
- **Type:** {first_clip.clip_type}
- **Score:** {first_clip.score:.2f}
- **Duration:** {first_clip.duration:.1f}s
- **Created:** {first_clip.created_at[:19]}
"""
        
        return info, video_path, gr.update(choices=choices, value=choices[0]), gr.update(interactive=True)
    
    def rate_clip_handler(self, clip_selector, rating):
        """Handle clip rating submission"""
        if not clip_selector:
            return "❌ Please select a clip to rate"
        
        # Extract clip ID from selector
        try:
            clip_id = int(clip_selector.split(":")[0].replace("ID", "").strip())
        except:
            return "❌ Invalid clip selection"
        
        if not rating:
            return "❌ Please select a rating (1-5 stars)"
        
        # Convert rating text to number
        rating_map = {
            "⭐ 1 - Poor": 1,
            "⭐⭐ 2 - Below Average": 2,
            "⭐⭐⭐ 3 - Average": 3,
            "⭐⭐⭐⭐ 4 - Good": 4,
            "⭐⭐⭐⭐⭐ 5 - Excellent": 5
        }
        
        rating_value = rating_map.get(rating)
        if not rating_value:
            return "❌ Invalid rating"
        
        # Update rating in database
        success = self.clip_manager.rate_clip(clip_id, rating_value)
        
        if success:
            # Attempt auto-training if enough ratings
            training_triggered = auto_train_if_ready(self.clip_manager, min_samples=10)
            
            message = f"✅ Clip rated {rating_value} stars! Model will improve with this feedback."
            if training_triggered:
                message += "\n\n🎓 Model automatically retrained with your ratings!"
            
            return message
        else:
            return "❌ Failed to save rating"
    
    def download_clip_handler(self, clip_selector):
        """Handle clip download"""
        if not clip_selector:
            return None, "❌ Please select a clip to download"
        
        try:
            clip_id = int(clip_selector.split(":")[0].replace("ID", "").strip())
        except:
            return None, "❌ Invalid clip selection"
        
        clip = self.clip_manager.db.get_clip(clip_id)
        if not clip or not Path(clip.filepath).exists():
            return None, "❌ Clip file not found"
        
        return clip.filepath, f"✅ Ready to download: {clip.filename}"
    
    def get_statistics_display(self):
        """Get formatted statistics for display"""
        stats = self.clip_manager.get_statistics()
        training_progress = self.model_trainer.get_training_progress()
        
        output = f"""
### 📊 Database Statistics

**Clips:**
- Total Clips: {stats['total_clips']}
- Rated Clips: {stats['rated_clips']}
- Unrated Clips: {stats['total_clips'] - stats['rated_clips']}
- Average Rating: {stats['average_rating']} ⭐

**Rating Distribution:**
"""
        
        for rating, count in sorted(stats.get('rating_distribution', {}).items()):
            stars = "⭐" * rating
            output += f"\n- {stars} ({rating}): {count} clips"
        
        output += "\n\n**Clips by Type:**"
        for clip_type, count in stats.get('clips_by_type', {}).items():
            output += f"\n- {clip_type.title()}: {count} clips"
        
        output += f"""

### 🎓 ML Model Status

**Training Status:**
- Model Trained: {'✅ Yes' if training_progress['model_trained'] else '❌ Not yet'}
- Audio Training Samples: {training_progress['audio_training_samples']}
- Video Training Samples: {training_progress['video_training_samples']}
- Ready for Training: {'✅ Yes' if training_progress['ready_for_training'] else f"❌ Need {10 - training_progress['rated_clips']} more ratings"}

**Note:** Model automatically retrains every 5 new ratings.
"""
        
        return output
    
    def manual_train_model(self):
        """Manually trigger model training"""
        try:
            progress = self.model_trainer.get_training_progress()
            
            if not progress['ready_for_training']:
                return f"❌ Need at least 10 rated clips to train. Currently have {progress['rated_clips']}."
            
            success = self.model_trainer.train_from_ratings(min_samples=10)
            
            if success:
                return "✅ Model training completed successfully! The AI will now use your ratings to improve highlight detection."
            else:
                return "❌ Training failed. Check logs for details."
        except Exception as e:
            logger.error(f"Manual training failed: {e}")
            return f"❌ Training error: {str(e)}"
    
    def create_interface(self):
        """Create the Gradio interface"""
        
        with gr.Blocks(
            theme=gr.themes.Soft(
                primary_hue="blue",
                secondary_hue="purple",
            ),
            title="Kick Clip Generator - ML-Powered Highlights"
        ) as interface:
            
            gr.Markdown("""
# 🎬 Kick Stream Clip Generator
### AI-Powered Highlight Detection with Continuous Learning

Generate highlight clips from Kick streams using advanced audio and video analysis.
The ML model improves over time as you rate clips!
""")
            
            with gr.Tabs():
                # Tab 1: Generate Clips
                with gr.Tab("🎥 Generate Clips"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            stream_url = gr.Textbox(
                                label="🔗 Stream URL",
                                placeholder="https://kick.com/stream-url or direct video URL",
                                lines=1
                            )
                            
                            with gr.Row():
                                clip_duration = gr.Slider(
                                    minimum=10,
                                    maximum=60,
                                    value=30,
                                    step=5,
                                    label="⏱️ Clip Duration (seconds)"
                                )
                                
                                min_gap = gr.Slider(
                                    minimum=5,
                                    maximum=60,
                                    value=10,
                                    step=5,
                                    label="📏 Minimum Gap Between Highlights (seconds)"
                                )
                            
                            with gr.Row():
                                max_audio_clips = gr.Slider(
                                    minimum=1,
                                    maximum=25,
                                    value=10,
                                    step=1,
                                    label="🎵 Max Audio Clips (1-25)"
                                )
                                
                                max_video_clips = gr.Slider(
                                    minimum=1,
                                    maximum=25,
                                    value=10,
                                    step=1,
                                    label="🎬 Max Video Clips (1-25)"
                                )
                            
                            with gr.Row():
                                start_minute = gr.Number(
                                    minimum=0,
                                    value=0,
                                    label="⏩ Start Minute (0 = from beginning)",
                                    info="Start analyzing from this minute"
                                )
                                
                                end_minute = gr.Number(
                                    minimum=0,
                                    value=0,
                                    label="⏸️ End Minute (0 = until end)",
                                    info="Stop analyzing at this minute"
                                )
                            
                            gr.Markdown("💡 **Tips:** Total clips limited to 50 max. Use time range to analyze specific portions of long videos.")
                            
                            analyze_btn = gr.Button("🔍 Analyze Stream", variant="primary", size="lg")
                        
                        with gr.Column(scale=1):
                            gr.Markdown("""
### 📊 Features

**Audio Analysis:**
- Volume & energy detection
- Voice excitement levels
- Spectral analysis
- Beat detection

**Video Analysis:**
- Motion detection
- Visual complexity
- Action recognition
- Scene changes

**ML Learning:**
- Continuous improvement
- Pattern recognition
- Score optimization
""")
                    
                    gr.Markdown("---")
                    
                    # Results section
                    with gr.Row():
                        analysis_output = gr.Markdown(label="Analysis Results")
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 🎵 Audio Highlights")
                            audio_table = gr.Dataframe(
                                headers=['Rank', 'Type', 'Start Time', 'Duration', 'Score'],
                                label="Top Audio Moments"
                            )
                        
                        with gr.Column():
                            gr.Markdown("### 🎬 Video Highlights")
                            video_table = gr.Dataframe(
                                headers=['Rank', 'Type', 'Start Time', 'Duration', 'Score'],
                                label="Top Video Moments"
                            )
                    
                    gr.Markdown("---")
                    
                    # Clip generation section
                    gr.Markdown("## 🎞️ Generate Clips")
                    
                    with gr.Row():
                        highlight_type = gr.Radio(
                            choices=["Audio Only", "Video Only", "Both"],
                            value="Both",
                            label="Select Highlight Type"
                        )
                        
                        generate_btn = gr.Button(
                            "🎬 Generate Clips",
                            variant="secondary",
                            size="lg",
                            interactive=False
                        )
                    
                    with gr.Row():
                        generation_output = gr.Markdown()
                    
                    with gr.Row():
                        clip_preview = gr.Video(label="📺 Clip Preview", interactive=False)
                    
                    # Gallery placeholder for updates
                    clip_gallery = gr.Gallery(label="Recent Clips", visible=False)
                
                # Tab 2: View & Rate Clips
                with gr.Tab("⭐ View & Rate Clips"):
                    gr.Markdown("""
## Rate Your Clips to Improve the Model

Your ratings help the AI learn what makes a great highlight! Rate clips from 1-5 stars.
""")
                    
                    with gr.Row():
                        load_clips_btn = gr.Button("📥 Load Clips for Rating", variant="primary", size="lg")
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            rating_clip_info = gr.Markdown("Click 'Load Clips for Rating' to begin")
                            rating_video = gr.Video(label="📺 Clip to Rate", interactive=False)
                        
                        with gr.Column(scale=1):
                            clip_selector = gr.Dropdown(
                                label="Select Clip",
                                choices=[],
                                interactive=False
                            )
                            
                            rating_choice = gr.Radio(
                                choices=[
                                    "⭐ 1 - Poor",
                                    "⭐⭐ 2 - Below Average",
                                    "⭐⭐⭐ 3 - Average",
                                    "⭐⭐⭐⭐ 4 - Good",
                                    "⭐⭐⭐⭐⭐ 5 - Excellent"
                                ],
                                label="Rate this clip",
                                value=None
                            )
                            
                            submit_rating_btn = gr.Button("✅ Submit Rating", variant="primary")
                            rating_status = gr.Markdown()
                    
                    gr.Markdown("---")
                    
                    gr.Markdown("## 📊 Statistics & Training")
                    
                    with gr.Row():
                        refresh_stats_btn = gr.Button("🔄 Refresh Statistics", variant="secondary")
                        train_model_btn = gr.Button("🎓 Train Model Now", variant="primary")
                    
                    stats_display = gr.Markdown()
                    train_status = gr.Markdown()
                
                # Tab 3: Browse & Download Clips
                with gr.Tab("📂 Browse & Download"):
                    gr.Markdown("""
## Browse All Generated Clips

View, download, and manage your clip library.
""")
                    
                    with gr.Row():
                        refresh_gallery_btn = gr.Button("🔄 Refresh Gallery", variant="primary")
                    
                    browse_gallery = gr.Gallery(
                        label="Clip Gallery",
                        columns=4,
                        height="auto",
                        object_fit="contain"
                    )
                    
                    gr.Markdown("### 💾 Download Clip")
                    
                    with gr.Row():
                        download_selector = gr.Dropdown(
                            label="Select Clip to Download",
                            choices=[]
                        )
                        download_btn = gr.Button("⬇️ Download", variant="secondary")
                    
                    with gr.Row():
                        download_file = gr.File(label="Downloaded Clip")
                        download_status = gr.Markdown()
            
            # Advanced settings (outside tabs)
            with gr.Accordion("⚙️ Advanced Settings", open=False):
                gr.Markdown("""
### Processing Configuration

- **Chunk Duration:** Streams are processed in 30-second chunks to avoid downloading full videos
- **Overlap:** 5-second overlap between chunks ensures no highlights are missed
- **Frame Skip:** Every 5th frame is analyzed for optimal performance
- **ML Model:** Automatically saves and improves with each stream processed

### Error Handling

- **403 Errors:** Automatic retry with exponential backoff
- **User Agent Rotation:** Prevents blocking
- **Graceful Degradation:** Continues processing even if individual chunks fail
""")
            
            # Event handlers - Generate Tab
            analyze_btn.click(
                fn=self.process_stream_wrapper,
                inputs=[stream_url, clip_duration, min_gap, max_audio_clips, max_video_clips, start_minute, end_minute],
                outputs=[analysis_output, audio_table, video_table, generate_btn, clip_preview]
            )
            
            generate_btn.click(
                fn=self.generate_clips_wrapper,
                inputs=[stream_url, highlight_type],
                outputs=[generation_output, clip_preview, clip_gallery]
            )
            
            # Event handlers - Rating Tab
            load_clips_btn.click(
                fn=self.load_clips_for_rating,
                inputs=[],
                outputs=[rating_clip_info, rating_video, clip_selector, submit_rating_btn]
            )
            
            submit_rating_btn.click(
                fn=self.rate_clip_handler,
                inputs=[clip_selector, rating_choice],
                outputs=[rating_status]
            )
            
            refresh_stats_btn.click(
                fn=self.get_statistics_display,
                inputs=[],
                outputs=[stats_display]
            )
            
            train_model_btn.click(
                fn=self.manual_train_model,
                inputs=[],
                outputs=[train_status]
            )
            
            # Event handlers - Browse Tab
            refresh_gallery_btn.click(
                fn=self._get_clip_gallery_update,
                inputs=[],
                outputs=[browse_gallery]
            )
            
            download_btn.click(
                fn=self.download_clip_handler,
                inputs=[download_selector],
                outputs=[download_file, download_status]
            )
            
            # Footer
            gr.Markdown("""
---
### 💡 Tips

1. **Stream URLs:** Works with direct video URLs, M3U8 streams, and Kick stream links
2. **Processing Time:** Depends on stream length (typically 1-2 minutes per hour of content)
3. **Rate Clips:** The more clips you rate, the better the ML model becomes at finding highlights
4. **Output:** Clips are saved in the `output_clips/` directory and tracked in the database

### 🔧 Troubleshooting

- **403 Errors:** The system automatically retries with different headers
- **Slow Processing:** Reduce clip duration or increase minimum gap
- **No Highlights:** Try adjusting sensitivity or check stream quality

**Made with ❤️ using Gradio, FFmpeg, and Machine Learning**
""")
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface"""
        interface = self.create_interface()
        interface.launch(**kwargs)


def main():
    """Main entry point"""
    app = GradioInterface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
