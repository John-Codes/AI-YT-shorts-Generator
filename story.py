import subprocess
from generate_image import generate_image  # Import the generate_image function
import os

text_file = 'text_content.txt'
output_video_file = 'output_video.mp4'
output_dir = 'vid_output'
os.makedirs(output_dir, exist_ok=True)

# Read content from text file
with open(text_file, 'r') as f:
    text_content = [line.strip() for line in f]

image_files = []
for i, text in enumerate(text_content):
    output_path = os.path.join(output_dir, f'output_{i}.png')
    generate_image(text_content=[text], output_path=output_path)
    image_files.append(output_path)

# Construct the ffmpeg command
ffmpeg_cmd = [
    'ffmpeg',
    '-framerate', '1/1',  # Ensure each image lasts 1 second
    '-i', os.path.join(output_dir, 'output_%d.png'),  # Input image sequence
    '-vf', 'crop=w=ih*9/16:h=iw', # Crop to 9:16 aspect ratio
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-b:v', '10M',  # Set video bitrate to 10 Mbps
    os.path.join(output_dir, output_video_file),
]

subprocess.run(ffmpeg_cmd)

# Copy the normal size video
import shutil
normal_video_path = os.path.join(output_dir, output_video_file)
shorts_video_path = os.path.join(output_dir, 'shorts_' + output_video_file)
shutil.copy2(normal_video_path, shorts_video_path)

# Construct the ffmpeg command for YouTube Shorts
ffmpeg_shorts_cmd = [
    'ffmpeg',
    '-i', shorts_video_path,
    '-vf', 'crop=9:16',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-b:v', '10M',
    os.path.join(output_dir, 'shorts_' + output_video_file) + '.mp4',
]

subprocess.run(ffmpeg_shorts_cmd)
