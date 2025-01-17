import os
import subprocess
import glob

def create_text_video(text, output_path, duration=1, font_size=60, font_color='white'):
    command = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c=black@0.0:s=1920x1080', # Transparent background
        '-vf', f"drawtext=text='{text}':fontcolor={font_color}:fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2",
        '-t', str(duration),
        '-pix_fmt', 'yuva420p',
        output_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Text video created at {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating text video: {e}")
        print(f"FFmpeg stdout: {e.stdout}")
        print(f"FFmpeg stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def create_video(image_folder="output/frames", output_video="output/videos/output.mp4", frame_duration=0.1):
    os.makedirs("output/videos", exist_ok=True)
    sentence_images = sorted(glob.glob(os.path.join(image_folder, "genImg_Sentence_*.png")))
    all_frames = []

    for sentence_image_path in sentence_images:
        base_filename = os.path.splitext(os.path.basename(sentence_image_path))[0]
        sentence_number = base_filename.split("_")[-1]
        sx_frame_folder = os.path.join(image_folder, f"S{sentence_number}")
        sx_frames = sorted(glob.glob(os.path.join(sx_frame_folder, "S*_size_*.png")))

        if sx_frames:
            background_image_path = os.path.join("output", "genImg", f"sentence_{sentence_number}.png")
            output_with_bg = os.path.join("output", "videos", f"S{sentence_number}_with_bg.mp4")
            
            if os.path.exists(background_image_path):
                command = [
                    'ffmpeg', '-y',
                    '-framerate', f'1/{frame_duration}',
                    '-i', os.path.join(sx_frame_folder, 'S%d_size_*.png'),
                    '-loop', '1', '-i', background_image_path,
                    '-shortest',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    output_with_bg
                ]
                try:
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    all_frames.append(output_with_bg)
                    print(f"Created video with background: {output_with_bg}")
                except subprocess.CalledProcessError as e:
                    print(f"Error creating video with background: {e}")
                    print(f"FFmpeg stdout: {e.stdout}")
                    print(f"FFmpeg stderr: {e.stderr}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            else:
                print(f"Background image not found: {background_image_path}")
        else:
            print(f"No Sx frames found for sentence: {sentence_number}")
            

    # Combine the videos with backgrounds
    if all_frames:
        num_frames = len(all_frames)
        print(f"Starting final video creation with {num_frames} video files.")
        # Combine videos into a final video using concat demuxer
        list_file_path = os.path.join("output", "videos", "concat_list.txt")
        with open(list_file_path, 'w') as f:
            for frame in all_frames:
                f.write(f"file '{frame}'\n")

        command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file_path,
            '-c', 'copy',
            output_video
        ]

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
    else:
        print("No videos with backgrounds were generated.")

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
