import torch
from diffusers import StableDiffusion3Pipeline

# Load the model
pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3.5-large",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)
if torch.cuda.is_available():
    pipe.enable_model_cpu_offload()
else:
    pipe.to("cpu")

# Generate an image
prompt = "A cute bunny white furry make him a USA marine with armor and sabing a kid in his arms make him humanoide like but with rabit head real fur and everything.  "
image = pipe(prompt, num_inference_steps=50, guidance_scale=7.0).images[0]

# Save the image
image.save("output.png")
print("Image saved as output.png")
