import os
import subprocess
import glob

import os
import subprocess
import glob
import json

def get_video_duration(video_path):
    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        output_json = json.loads(result.stdout)
        if 'format' in output_json and 'duration' in output_json['format']:
            return float(output_json['format']['duration'])
    return 0

def create_text_video(text, output_path, duration=1, font_size=60, font_color='white'):
    command = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'color=c=black@0.0:s=1920x1080:a=1', # Transparent background with alpha channel
        '-vf', f"drawtext=text='{text}':fontcolor={font_color}:fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2",
        '-t', str(duration),
        '-pix_fmt', 'yuva420p', # Ensure pixel format supports transparency
        '-vcodec', 'libx264', # Use libx264 for encoding
        '-acodec', 'none', # No audio
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

def create_video_with_background(text_video_path, background_image_path, output_video_path):
    duration = get_video_duration(text_video_path)
    if duration <= 0:
        print("Could not determine text video duration or duration is zero.")
        return

    command = [
        'ffmpeg',
        '-i', background_image_path,
        '-i', text_video_path,
        '-t', str(duration),
        '-map', '0:v',
        '-map', '1:v',
        '-filter_complex', 'overlay=0:0',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_video_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Video with background created at {output_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating video with background: {e}")
        print(f"FFmpeg stdout: {e.stdout}")
        print(f"FFmpeg stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_video(image_folder, output_video, frame_duration=0.1): # Modified output_video parameter
    # os.makedirs("output/videos", exist_ok=True) # sentencevideos dir is created in main.py
    sentences_folders = sorted(glob.glob(os.path.join(image_folder, "S*")))
    # all_sentence_videos = [] # Removed sentence video combining

    print(f"Sentences folders found: {sentences_folders}") # Debugging line

    for sentence_folder in sentences_folders:
        sentence_number = sentence_folder.split(os.sep)[-1].replace("S", "")
        sx_frames_folder = sentence_folder # sx_frames_folder is now sentence_folder
        sx_frames = sorted(glob.glob(os.path.join(sx_frames_folder, f"S{sentence_number}_size_*.png")))

        print(f"Sentence folder: {sentence_folder}") # Debugging line
        print(f"Frames folder: {sx_frames_folder}") # Debugging line
        print(f"Frames found: {sx_frames}") # Debugging line


        if sx_frames:
            background_image_path = os.path.join("output", "AIBackgroundImage", f"sentence_{sentence_number}.png")
            output_with_bg_video = os.path.join("output", "videos", f"S{sentence_number}_with_bg.mp4") # Changed variable name to be more descriptive - not used anymore
            text_video_path = os.path.join("output", "videos", f"text_S{sentence_number}.mp4") # not used anymore
            sentence_text_filepath = os.path.join(sentence_folder, "sentence.txt")

            if os.path.exists(background_image_path):
                if os.path.exists(sentence_text_filepath):
                    with open(sentence_text_filepath, 'r') as f:
                        sentence_text = f.read().strip()
                    # Create text video with transparent background - not used anymore
                    # create_text_video(sentence_text, text_video_path, duration=5) # Fixed duration to 5 seconds per sentence for now - not used anymore
                    # Generate video with background
                    # create_video_with_background(text_video_path, background_image_path, output_with_bg_video) # not used anymore
                    # all_sentence_videos.append(output_with_bg_video) # not used anymore
                    # print(f"Created video with background for sentence {sentence_number}: {output_with_bg_video}") # not used anymore

                    # Directly create video from frames and background
                    command = [
                        'ffmpeg',
                        '-framerate', '1/5', # 5 seconds per frame
                        '-i', os.path.join(sx_frames_folder, f'S{sentence_number}_size_%d.png'),
                        '-loop', '1',
                        '-i', background_image_path,
                        '-map', '0:v',
                        '-map', '1:v',
                        '-filter_complex', 'overlay=0:0',
                        '-t', '5', # 5 seconds duration
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        output_video # Use provided output_video path
                    ]
                    try:
                        subprocess.run(command, check=True, capture_output=True, text=True)
                        print(f"Video created for sentence {sentence_number} at: {output_video}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error creating video for sentence {sentence_number}: {e}")
                        print(f"FFmpeg stdout: {e.stdout}")
                        print(f"FFmpeg stderr: {e.stderr}")
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")


                else:
                    print(f"Sentence text file not found: {sentence_text_filepath}")
            else:
                print(f"Background image not found: {background_image_path}")
        else:
            print(f"No Sx frames found for sentence: {sentence_number}")

    # # Combine the sentence videos with backgrounds - Removed video combining
    # if all_sentence_videos: # Changed variable name - Removed video combining
    #     num_videos = len(all_sentence_videos) # Changed variable name - Removed video combining
    #     print(f"Starting final video creation with {num_videos} sentence videos.") # Updated print statement - Removed video combining
    #     # Combine videos into a final video using concat demuxer - Removed video combining
    #     list_file_path = os.path.join("output", "videos", "concat_list.txt") - Removed video combining
    #     with open(list_file_path, 'w') as f: - Removed video combining
    #         for video_file in all_sentence_videos: # Changed variable name - Removed video combining
    #             f.write(f"file '{video_file}'\n") - Removed video combining

    #     command = [  - Removed video combining
    #         'ffmpeg',  - Removed video combining
    #         '-f', 'concat',  - Removed video combining
    #         '-safe', '0',  - Removed video combining
    #         '-i', list_file_path,  - Removed video combining
    #         '-c', 'copy',  - Removed video combining
    #         output_video  - Removed video combining
    #     ]  - Removed video combining

    #     try:  - Removed video combining
    #         subprocess.run(command, check=True, capture_output=True, text=True)  - Removed video combining
    #         print(f"Final video created at {output_video}") # Updated print statement - Removed video combining
    #     except subprocess.CalledProcessError as e:  - Removed video combining
    #         print(f"Error creating final video: {e}") # Updated print statement - Removed video combining
    #         print(f"FFmpeg stdout: {e.stdout}") - Removed video combining
    #         print(f"FFmpeg stderr: {e.stderr}") - Removed video combining
    #     except Exception as e:  - Removed video combining
    #         print(f"An unexpected error occurred during final video creation: {e}") # Updated print statement - Removed video combining
    #     finally:  - Removed video combining
    #         print("Final video creation process finished.") # Updated print statement - Removed video combining
    # else: - Removed video combining
    #     print("No sentence videos with backgrounds were generated.") # Updated print statement - Removed video combining


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
import os
import subprocess
import glob

import os
import subprocess
import glob
import json

def get_video_duration(video_path):
    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        output_json = json.loads(result.stdout)
        if 'format' in output_json and 'duration' in output_json['format']:
            return float(output_json['format']['duration'])
    return 0

def create_text_video(text, output_path, duration=1, font_size=60, font_color='white'):
    command = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'color=c=black@0.0:s=1920x1080:a=1', # Transparent background with alpha channel
        '-vf', f"drawtext=text='{text}':fontcolor={font_color}:fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2",
        '-t', str(duration),
        '-pix_fmt', 'yuva420p', # Ensure pixel format supports transparency
        '-vcodec', 'libx264', # Use libx264 for encoding
        '-acodec', 'none', # No audio
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

def create_video_with_background(text_video_path, background_image_path, output_video_path): # not used anymore
    duration = get_video_duration(text_video_path) # not used anymore
    if duration <= 0: # not used anymore
        print("Could not determine text video duration or duration is zero.") # not used anymore
        return # not used anymore

    command = [ # not used anymore
        'ffmpeg', # not used anymore
        '-i', background_image_path, # not used anymore
        '-i', text_video_path, # not used anymore
        '-t', str(duration), # not used anymore
        '-map', '0:v', # not used anymore
        '-map', '1:v', # not used anymore
        '-filter_complex', 'overlay=0:0', # not used anymore
        '-c:v', 'libx264', # not used anymore
        '-pix_fmt', 'yuv420p', # not used anymore
        '-shortest', # not used anymore
        output_video_path # not used anymore
    ] # not used anymore
    try: # not used anymore
        subprocess.run(command, check=True, capture_output=True, text=True) # not used anymore
        print(f"Video with background created at {output_video_path}") # not used anymore
    except subprocess.CalledProcessError as e: # not used anymore
        print(f"Error creating video with background: {e}") # not used anymore
        print(f"FFmpeg stdout: {e.stdout}") # not used anymore
        print(f"FFmpeg stderr: {e.stderr}") # not used anymore
    except Exception as e: # not used anymore
        print(f"An unexpected error occurred: {e}") # not used anymore


def create_video(image_folder, output_video, frame_duration=0.1): # Modified output_video parameter
    # os.makedirs("output/videos", exist_ok=True) # sentencevideos dir is created in main.py
    sentences_folders = sorted(glob.glob(os.path.join(image_folder, "S*")))
    # all_sentence_videos = [] # Removed sentence video combining

    print(f"Sentences folders found: {sentences_folders}") # Debugging line

    for sentence_folder in sentences_folders:
        sentence_number = sentence_folder.split(os.sep)[-1].replace("S", "")
        sx_frames_folder = sentence_folder # sx_frames_folder is now sentence_folder
        sx_frames = sorted(glob.glob(os.path.join(sx_frames_folder, f"S{sentence_number}_size_*.png")))

        print(f"Sentence folder: {sentence_folder}") # Debugging line
        print(f"Frames folder: {sx_frames_folder}") # Debugging line
        print(f"Frames found: {sx_frames}") # Debugging line


        if sx_frames:
            background_image_path = os.path.join("output", "AIBackgroundImage", f"sentence_{sentence_number}.png")
            output_with_bg_video = os.path.join("output", "videos", f"S{sentence_number}_with_bg.mp4") # Changed variable name to be more descriptive - not used anymore
            text_video_path = os.path.join("output", "videos", f"text_S{sentence_number}.mp4") # not used anymore
            sentence_text_filepath = os.path.join(sentence_folder, "sentence.txt")

            if os.path.exists(background_image_path):
                if os.path.exists(sentence_text_filepath):
                    with open(sentence_text_filepath, 'r') as f:
                        sentence_text = f.read().strip()
                    # Create text video with transparent background - not used anymore
                    # create_text_video(sentence_text, text_video_path, duration=5) # Fixed duration to 5 seconds per sentence for now - not used anymore
                    # Generate video with background - not used anymore
                    # create_video_with_background(text_video_path, background_image_path, output_with_bg_video) # not used anymore
                    # all_sentence_videos.append(output_with_bg_video) # not used anymore
                    # print(f"Created video with background for sentence {sentence_number}: {output_with_bg_video}") # not used anymore

                    # Directly create video from frames and background
                    command = [
                        'ffmpeg',
                        '-framerate', '1/5', # 5 seconds per frame
                        '-i', os.path.join(sx_frames_folder, f'S{sentence_number}_size_%d.png'),
                        '-loop', '1',
                        '-i', background_image_path,
                        '-map', '0:v',
                        '-map', '1:v',
                        '-filter_complex', 'overlay=0:0',
                        '-t', '5', # 5 seconds duration
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        output_video # Use provided output_video path
                    ]
                    try:
                        subprocess.run(command, check=True, capture_output=True, text=True)
                        print(f"Video created for sentence {sentence_number} at: {output_video}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error creating video for sentence {sentence_number}: {e}")
                        print(f"FFmpeg stdout: {e.stdout}")
                        print(f"FFmpeg stderr: {e.stderr}")
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")


                else:
                    print(f"Sentence text file not found: {sentence_text_filepath}")
            else:
                print(f"Background image not found: {background_image_path}")
        else:
            print(f"No Sx frames found for sentence: {sentence_number}")


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
import os
import subprocess
import glob

import os
import subprocess
import glob
import json

def get_video_duration(video_path):
    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        output_json = json.loads(result.stdout)
        if 'format' in output_json and 'duration' in output_json['format']:
            return float(output_json['format']['duration'])
    return 0

def create_text_video(text, output_path, duration=1, font_size=60, font_color='white'):
    command = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'color=c=black@0.0:s=1920x1080:a=1', # Transparent background with alpha channel
        '-vf', f"drawtext=text='{text}':fontcolor={font_color}:fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2",
        '-t', str(duration),
        '-pix_fmt', 'yuva420p', # Ensure pixel format supports transparency
        '-vcodec', 'libx264', # Use libx264 for encoding
        '-acodec', 'none', # No audio
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

def create_video_with_background(text_video_path, background_image_path, output_video_path):
    duration = get_video_duration(text_video_path)
    if duration <= 0:
        print("Could not determine text video duration or duration is zero.")
        return

    command = [
        'ffmpeg',
        '-i', background_image_path,
        '-i', text_video_path,
        '-t', str(duration),
        '-map', '0:v',
        '-map', '1:v',
        '-filter_complex', 'overlay=0:0',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_video_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Video with background created at {output_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating video with background: {e}")
        print(f"FFmpeg stdout: {e.stdout}")
        print(f"FFmpeg stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_video(image_folder, output_video="output/videos/output.mp4", frame_duration=0.1):
    # os.makedirs("output/videos", exist_ok=True) # sentencevideos dir is created in main.py
    sentences_folders = sorted(glob.glob(os.path.join(image_folder, "S*")))
    all_sentence_videos = []

    print(f"Sentences folders found: {sentences_folders}") # Debugging line

    for sentence_folder in sentences_folders:
        sentence_number = sentence_folder.split(os.sep)[-1].replace("S", "")
        sx_frames_folder = sentence_folder # sx_frames_folder is now sentence_folder
        sx_frames = sorted(glob.glob(os.path.join(sx_frames_folder, f"S{sentence_number}_size_*.png")))

        print(f"Sentence folder: {sentence_folder}") # Debugging line
        print(f"Frames folder: {sx_frames_folder}") # Debugging line
        print(f"Frames found: {sx_frames}") # Debugging line


        if sx_frames:
            background_image_path = os.path.join("output", "AIBackgroundImage", f"sentence_{sentence_number}.png")
            output_with_bg_video = os.path.join("output", "videos", f"S{sentence_number}_with_bg.mp4") # Changed variable name to be more descriptive
            text_video_path = os.path.join("output", "videos", f"text_S{sentence_number}.mp4")
            sentence_text_filepath = os.path.join(sentence_folder, "sentence.txt")

            if os.path.exists(background_image_path):
                if os.path.exists(sentence_text_filepath):
                    with open(sentence_text_filepath, 'r') as f:
                        sentence_text = f.read().strip()
                    # Create text video with transparent background
                    create_text_video(sentence_text, text_video_path, duration=5) # Fixed duration to 5 seconds per sentence for now
                    # Generate video with background
                    create_video_with_background(text_video_path, background_image_path, output_with_bg_video)
                    all_sentence_videos.append(output_with_bg_video)
                    print(f"Created video with background for sentence {sentence_number}: {output_with_bg_video}")
                else:
                    print(f"Sentence text file not found: {sentence_text_filepath}")
            else:
                print(f"Background image not found: {background_image_path}")
        else:
            print(f"No Sx frames found for sentence: {sentence_number}")

    # Combine the sentence videos with backgrounds
    if all_sentence_videos: # Changed variable name
        num_videos = len(all_sentence_videos) # Changed variable name
        print(f"Starting final video creation with {num_videos} sentence videos.") # Updated print statement
        # Combine videos into a final video using concat demuxer
        list_file_path = os.path.join("output", "videos", "concat_list.txt")
        with open(list_file_path, 'w') as f:
            for video_file in all_sentence_videos: # Changed variable name
                f.write(f"file '{video_file}'\n")

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
            print(f"Final video created at {output_video}") # Updated print statement
        except subprocess.CalledProcessError as e:
            print(f"Error creating final video: {e}") # Updated print statement
            print(f"FFmpeg stdout: {e.stdout}")
            print(f"FFmpeg stderr: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred during final video creation: {e}") # Updated print statement
        finally:
            print("Final video creation process finished.") # Updated print statement
    else:
        print("No sentence videos with backgrounds were generated.") # Updated print statement


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
