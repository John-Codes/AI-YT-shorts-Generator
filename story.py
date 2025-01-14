import subprocess
from generate_image import generate_image
from txt import text

sentences = [
    "This is the first sentence for the video.",
    "Here is the second sentence, a bit longer.",
    "The third sentence is quite short.",
    "And this is the final sentence to complete the story."
]

image_files = []
for i, sentence in enumerate(sentences):
    text_instance = text(sentence)
    chunks = text_instance.get_chunks()
    image_path = f"output_{i + 1}.png"
    print(f"Calling generate_image with output_path: {image_path}")
    generate_image(text_content=chunks, output_path=image_path)
    print(f"Generated image: {image_path}")
    image_files.append(image_path)

# Construct the ffmpeg command
ffmpeg_cmd = [
    'ffmpeg',
    '-framerate', '1',  # Set the frame rate
    '-i', 'output_%d.png',  # Input image pattern
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    'output_video.mp4'
]

print(f"Executing ffmpeg command: {' '.join(ffmpeg_cmd)}")
subprocess.run(ffmpeg_cmd)
print("Video saved as output_video.mp4")
