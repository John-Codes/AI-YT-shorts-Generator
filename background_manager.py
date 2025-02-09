from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import logging
import os

logger = logging.getLogger(__name__)

class BackgroundManager:
    def __init__(self, use_image_bg: bool):
        self.use_image_bg = use_image_bg
        logger.info(f"BackgroundManager initialized with use_image_bg={use_image_bg}")

    def process(self, sentence_idx: int, bg_path: str, duration: float):
        """Handle both background types with index-based processing"""
        output_path = f"assets/processed/S{sentence_idx}.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            if self.use_image_bg:
                bg = ImageClip(bg_path).set_duration(duration)
            else:
                bg = VideoFileClip(bg_path).subclip(0, duration).set_audio(None) # Remove audio from background video

            text_clip = VideoFileClip(f"assets/videos/S{sentence_idx}.mp4").set_position('center')
            final_clip = CompositeVideoClip([bg, text_clip])
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=25)
            logger.info(f"S{sentence_idx} background processed successfully to {output_path}")
        except Exception as e:
            logger.error(f"S{sentence_idx} background processing failed: {str(e)}")
            return None
