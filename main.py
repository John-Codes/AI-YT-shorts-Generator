from generate_image import generate_image
import os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from create_video import create_video, crop_video

nltk.download('punkt')

text_file = 'text_content.txt'
output_dir = 'output/frames'
os.makedirs(output_dir, exist_ok=True)

# Read content from text file
with open(text_file, 'r') as f:
    text_content = f.read()

sentences = sent_tokenize(text_content)

frame_count = 0
for i, sentence in enumerate(sentences):
    # Generate base image for the sentence
    base_image_path = os.path.join("output", "genImg", f'sentence_{i}.png')
    generate_image(text_content=[sentence], output_path=base_image_path, base_image=None) # Modified call

    words = word_tokenize(sentence)
    for j, word in enumerate(words):
        word_image_path = os.path.join("output", "frames", f'sentence_{i}_word_{j:02d}.png')
        # Need to modify generate_image to handle single word and base image
        generate_image(text_content=[word], output_path=word_image_path, base_image=base_image_path)
        frame_count += 1

print(f"Generated {frame_count} frames.")

create_video()
crop_video(output_video="output/videos/output_cropped.mp4")
