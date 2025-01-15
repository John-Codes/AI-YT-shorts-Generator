import torch
from diffusers import StableDiffusion3Pipeline
from PIL import Image, ImageDraw, ImageFont
import time
import os

# Load the model
pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3.5-large",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)
if torch.cuda.is_available():
    pipe.enable_model_cpu_offload()
else:
    pipe.to("cpu")

def is_dark(color, threshold=100):
    return sum(color) < threshold

def generate_image(text_content, output_path, sentence_index=0, word_index=0, width=1024, height=1024, base_image=None):
    font_size = 50
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text_color = (0, 0, 0)  # Black
    if base_image is None:
        output_path = os.path.join("output", "genImg", os.path.basename(output_path))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Generate base image
        while True:
            image = pipe(prompt="An abstract background", num_inference_steps=20, guidance_scale=7.0, width=width, height=height).images[0]
            img_width, img_height = image.size
            center_x, center_y = img_width // 2, img_height // 2
            center_color = image.getpixel((center_x, center_y))
            if not is_dark(center_color):
                break
        image.save(output_path)
        print(f"Base image saved as {output_path}")
    else:
        output_path_base = os.path.join("output", "frames", f"S{sentence_index}")
        os.makedirs(output_path_base, exist_ok=True)
        # Add word to base image with animation
        word = text_content[0]
        base = Image.open(base_image).convert("RGBA")
        img_width, img_height = base.size
        # Create a transparent image for the animation
        animation_base = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(animation_base)
        bbox = draw.textbbox((0, 0), word, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = img_width / 2 - text_width / 2
        text_y = img_height / 2 - text_height / 2

        for size in range(10, font_size + 1, 5):
            animated_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            temp_image = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            d = ImageDraw.Draw(temp_image)
            bbox_anim = d.textbbox((0, 0), word, font=animated_font)
            text_width_anim = bbox_anim[2] - bbox_anim[0]
            text_height_anim = bbox_anim[3] - bbox_anim[1]
            text_x_anim = img_width / 2 - text_width_anim / 2
            text_y_anim = img_height / 2 - text_height_anim / 2
            d.text((text_x_anim, text_y_anim), word, fill=(0, 0, 0), font=animated_font)
            output_path = os.path.join(output_path_base, f"S{sentence_index}_size_{size}.png") # Save animated frames with transparent background
            temp_image.save(output_path)

        print(f"Word animation frames saved in {output_path_base}")

if __name__ == "__main__":
    with open("text_content.txt", "r") as f:
        text_content = [line.strip() for line in f]
    generate_image(text_content=text_content, output_path="output/genImg/test.png")
