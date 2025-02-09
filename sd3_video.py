from diffusers import StableVideoDiffusionPipeline
import torch
import logging
import os
from PIL import Image

logger = logging.getLogger(__name__)

class SD3VideoGenerator:
    def __init__(self):
        try:
            self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                "stabilityai/stable-video-diffusion-img2vid-xt",
                torch_dtype=torch.float16
            ).to("cuda")
            self.pipeline.enable_sequential_cpu_offload() # VRAM optimization - sequential CPU offload
            self.pipeline.enable_model_cpu_offload()
            self.pipeline.enable_attention_slicing() # Enable attention slicing
            self.pipeline.enable_xformers_memory_efficient_attention()
            logger.info("SD3VideoGenerator initialized successfully.")
        except Exception as e:
            logger.error(f"SD3VideoGenerator initialization failed: {str(e)}")
            raise

    def generate(self, image_path: str, duration: float, sentence_idx: int) -> str:
        """Generate video from image with 4090-optimized settings"""
        try:
            num_frames = 25  # Reduced number of frames
            init_image = Image.open(image_path).convert("RGB")
            init_image = init_image.resize((64, 64)) # Keep reduced image size
            video_frames = self.pipeline(image=init_image, num_frames=num_frames).frames # Re-introduce num_frames
            path = f"assets/backgrounds/videos/S{sentence_idx}.mp4"
            self._save_video(video_frames, path)
            logger.info(f"S{sentence_idx} video generated successfully.")
            return path
        except Exception as e:
            logger.error(f"S{sentence_idx} video generation failed: {str(e)}")
            return None

    def _save_video(self, frames, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            import cv2
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            import numpy as np
            height, width = np.array(frames[0]).shape[:2]
            writer = cv2.VideoWriter(path, fourcc, 25.0, (width, height))
            print(f"Number of frames to save: {len(frames)}") # Print frame length before saving
            for frame in frames:
                numpy_frame = np.array(frame, dtype=np.uint8)
                writer.write(cv2.cvtColor(numpy_frame, cv2.COLOR_RGB2BGR))
            writer.release()
            logger.info(f"Video saved to {path} with {len(frames)} frames.")
            print(f"Video saved to {path} with {len(frames)} frames.") # Added print statement
        except Exception as e:
            logger.error(f"Video saving failed: {str(e)}")
            raise

if __name__ == "__main__":
    import subprocess
    from PIL import Image

    print("Starting video generation test...")

    # Execute nvidia-smi and print the output
    try:
        nvidia_smi_output = subprocess.check_output(['nvidia-smi'], encoding='utf-8')
        print("nvidia-smi output:\n", nvidia_smi_output)
    except FileNotFoundError:
        print("nvidia-smi not found. Please ensure it's installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing nvidia-smi: {e}")

    # Generate a dummy white image
    img = Image.new('RGB', (64, 64), color='white')
    dummy_image_path = "dummy_image.png"
    img.save(dummy_image_path)

    video_generator = SD3VideoGenerator()
    # Test with explicit num_frames
    video_generator_explicit_frames = SD3VideoGenerator()
    video_path_explicit_frames = video_generator_explicit_frames.generate(dummy_image_path, 0.1, 98) # Explicitly set duration to 0.1 second
    print(f"Generating test video with explicit frames, duration=0.1 second")
    if video_path_explicit_frames:
        print(f"Test video (explicit frames) generated successfully at: {video_path_explicit_frames}")
    else:
        print("Test video (explicit frames) generation failed.")
    print("Video generation test finished.")
