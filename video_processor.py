import os
import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips

def process_videos(videos_dict, originals_directory, clips_directory, final_serve_directory):
    for video_file, video_data in videos_dict.items():
        logging.info(f"Processing video: {video_file}")

        associated_tasks = video_data["associated_tasks"]
        logging.info(f"Associated tasks: {associated_tasks}")

        original_file_path = os.path.join(originals_directory, 'ticket', video_file)

        if not os.path.exists(original_file_path):
            logging.error(f"Video file not found: {original_file_path}")
            continue

        # Process each task associated with this video
        for task_idx, task in enumerate(associated_tasks):
            for group in task['clip_groups']:
                clips = []
                for clip_data in group['clips']:
                    clip_filename = process_clip(
                        original_file_path,
                        clip_data,
                        clips_directory,
                        task_idx,
                        group['group_id'],
                        os.path.basename(original_file_path)
                    )
                    clip_data['filename'] = clip_filename
                    clips.append(clip_filename)

                # Merge clips if necessary
                if group['merge_required']:
                    merged_filename = os.path.join(
                        clips_directory,
                        f"{os.path.splitext(os.path.basename(original_file_path))[0]}_merged_{group['group_id']}.mp4"
                    )
                    if clips:
                        merged_clip = concatenate_videoclips([VideoFileClip(clip) for clip in clips])
                        merged_clip.write_videofile(merged_filename, codec='libx264', audio_codec='aac')
                        logging.info(f"Merged clips saved to {merged_filename}")

                    final_filename = f"{os.path.splitext(os.path.basename(merged_filename))[0]}.mp4"
                    final_filepath = os.path.join(final_serve_directory, final_filename)

                    if os.path.exists(final_filepath):
                        logging.info(f"File {final_filepath} already exists. Overwriting it.")
                        os.remove(final_filepath)

                    os.rename(merged_filename, final_filepath)
                    logging.info(f"Final merged video saved to {final_filepath}")

                else:
                    for clip in clips:
                        final_clip_path = os.path.join(final_serve_directory, os.path.basename(clip))

                        if os.path.exists(final_clip_path):
                            logging.info(f"Clip {final_clip_path} already exists. Overwriting it.")
                            os.remove(final_clip_path)

                        os.rename(clip, final_clip_path)
                        logging.info(f"Clip moved to {final_clip_path}")

def process_clip(video_file, clip_data, clips_directory, task_idx, group_id, original_filename):
    """Extracts and processes a single clip from the video file."""
    start_time = clip_data['start_time']
    end_time = clip_data['end_time']

    clip = VideoFileClip(video_file).subclip(start_time, end_time)

    # Generate the clip filename based on the original filename
    clip_filename = os.path.join(
        clips_directory,
        f"{os.path.splitext(original_filename)[0]}_clip_{task_idx}_{group_id}_{clip_data['clip_id']}.mp4"
    )

    clip.write_videofile(clip_filename, codec='libx264', audio_codec='aac')
    logging.info(f"Clip saved to {clip_filename}")

    # Close audio reader to avoid WinError
    if hasattr(clip.audio, 'reader'):
        clip.audio.reader.close_proc()

    return clip_filename
