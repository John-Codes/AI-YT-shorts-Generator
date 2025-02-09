from diffusers import StableDiffusion3Pipeline
import torch
import logging

logger = logging.getLogger(__name__)

class SD3ImageGenerator:
    def __init__(self):
        try:
            self.pipeline = StableDiffusion3Pipeline.from_pretrained(
                "stabilityai/stable-diffusion-3-medium-diffusers",
                torch_dtype=torch.float16,
                variant="fp16"
            ).to("cuda")
            # self.pipeline.enable_model_cpu_offload() # VRAM optimization
            # self.pipeline.enable_xformers_memory_efficient_attention()
            print("Downloading Stable Diffusion 3 model...")
            logger.info("SD3ImageGenerator initialized successfully.")
        except Exception as e:
            logger.error(f"SD3ImageGenerator initialization failed: {str(e)}")
            raise

    def generate(self, prompt: str, sentence_idx: int) -> str:
        """Generate 512x512 image for testing"""
        try:
            image = self.pipeline(prompt=prompt, height=512, width=512).images[0]
            path = f"assets/backgrounds/images/S{sentence_idx}.png"
            image.save(path)
            torch.cuda.empty_cache() # Memory management
            logger.info(f"S{sentence_idx} image generated successfully.")
            return path
        except Exception as e:
            logger.error(f"S{sentence_idx} image generation failed: {str(e)}")
            return None

if __name__ == "__main__":
    generator = SD3ImageGenerator()
    image_path = generator.generate("A futuristic cityscape", 99)
    if image_path:
        print(f"Test image generated successfully at: {image_path}")
    else:
        print("Test image generation failed.")
