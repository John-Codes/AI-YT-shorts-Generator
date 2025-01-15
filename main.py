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
    generate_image(text_content=[sentence], output_path=os.path.join("output", "genImg", f'sentence_{i}.png')) # Generate base image
    words = word_tokenize(sentence)
    # Generate word animations for the sentence
    generate_image(text_content=words, output_path=os.path.join(output_dir, f'S{i}'), sentence_index=i, base_image=base_image_path)
    frame_count += len(words)

print(f"Generated {frame_count} frames.")

create_video()
crop_video(output_video="output/videos/output_cropped.mp4")
