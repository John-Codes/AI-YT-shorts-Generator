import os
import subprocess
import glob

def create_video(image_folder="output/frames", output_video="output/videos/output.mp4", frame_duration=0.1):
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

    num_frames = len(all_frames)
    print(f"Starting video creation with {num_frames} frames and a frame duration of {frame_duration} seconds.")
    # Combine images into a video using concat filter
    input_args = ' '.join([f'-i {f}' for f in all_frames])
    filter_complex_parts = []
    for i, frame in enumerate(all_frames):
        filter_complex_parts.append(f"[{i}:v]setpts={frame_duration}/TB[s{i}];")
    concat_inputs = "".join([f"[s{i}]" for i in range(num_frames)])
    concat_filter = f"{concat_inputs}concat=n={num_frames}:v=1:a=0,format=yuv420p[v]"
    filter_complex = "".join(filter_complex_parts) + concat_filter

    command = ['ffmpeg', '-y'] + \
              input_args.split() + \
              ['-filter_complex', filter_complex, '-map', '[v]', output_video]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Video created at {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
        print(f"FFmpeg stdout: {e.stdout}")
        print(f"FFmpeg stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Video creation process finished.")

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
