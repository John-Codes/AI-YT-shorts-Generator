import os
import subprocess
import glob

def create_video(image_folder="output/frames", output_video="output/videos/output.mp4", frame_rate=2):
    sentence_images = sorted(glob.glob(os.path.join(image_folder, "sentence_*.png")))
    all_frames = []

    for sentence_image_path in sentence_images:
        base_filename = os.path.splitext(os.path.basename(sentence_image_path))[0]
        word_frames = sorted(glob.glob(os.path.join(image_folder, f"{base_filename}_word_*.png")))
        animated_frames = []
        for word_frame in word_frames:
            animated_frames.extend(sorted(glob.glob(os.path.join(image_folder, word_frame.replace(".png", "_size_*.png")))))
            animated_frames.append(word_frame) # Add the final word frame

        all_frames.append(sentence_image_path) # Add the base sentence image
        all_frames.extend(animated_frames)

    if not all_frames:
        print("No image files found.")
        return

    # Combine images into a video
    command = ['ffmpeg', '-y']
    for frame_path in all_frames:
        command.extend(['-i', frame_path])

    input_args = ' '.join([f'-i {f}' for f in all_frames])
    concat_list = ' '.join([f'[{i}]' for i in range(len(all_frames))])
    concat_filter = f"concat=n={len(all_frames)}:v=1:a=0,format=yuv420p[v]"

    command = ['ffmpeg', '-y'] + \
              input_args.split() + \
              ['-filter_complex', concat_filter, '-map', '[v]', output_video]

    subprocess.run(command, check=True)
    print(f"Video created at {output_video}")

def crop_video(input_video="output/videos/output.mp4", output_video="output/videos/output_cropped.mp4"):
    # Crop the video to 9:16 aspect ratio
    command = [
        'ffmpeg',
        '-i', input_video,
        '-vf', "crop=9*ih/16:ih",
        output_video
    ]
    subprocess.run(command, check=True)
    print(f"Cropped video created at {output_video}")

if __name__ == "__main__":
    create_video()
    crop_video(output_video="output/videos/output_cropped.mp4")
