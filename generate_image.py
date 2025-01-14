import torch
from diffusers import StableDiffusion3Pipeline
from PIL import Image, ImageDraw, ImageFont

# Load the model
pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3.5-large",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)
if torch.cuda.is_available():
    pipe.enable_model_cpu_offload()
else:
    pipe.to("cpu")

def generate_image(text_content, output_path, width=1024, height=1024, prompt="An abstract background"):
    # Generate an image with specified dimensions
    image = pipe(prompt, num_inference_steps=50, guidance_scale=7.0, width=width, height=height).images[0]

    # Initialize drawing context
    draw = ImageDraw.Draw(image)
    width, height = image.size
    font_size = 50
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text_color = (0, 0, 0)  # Black

    # Calculate total text height
    total_text_height = len(text_content) * font_size * 1.2

    # Starting y position for the text
    current_y = (height - total_text_height) / 2

    # Add text to the image
    for line in text_content:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) / 2
        draw.text((text_x, current_y), line, fill=text_color, font=font)
        current_y += text_height * 1.2

    # Save the image
    image.save(output_path)
    print(f"Image saved as {output_path}")

if __name__ == "__main__":
    # Example usage
    text_content = ["This is a test", "with multiple lines"]
    generate_image(text_content=text_content, output_path="output.png")
