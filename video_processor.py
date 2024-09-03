import os
import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips

def process_videos(uuid_mapping, originals_directory, clips_directory, final_serve_directory):
    for uuid, data in uuid_mapping.items():
        logging.info(f"Processing videos for UUID: {uuid}")

        task_directory = data['path']
        downloaded_files = data['downloaded_files']
        associated_task = data['associated_task']

        # Move downloaded files to the originals directory
        original_files = []
        for file in downloaded_files:
            original_file_path = os.path.join(originals_directory, os.path.basename(file))
            os.rename(os.path.join(task_directory, file), original_file_path)
            original_files.append(original_file_path)

        for group in associated_task['clip_groups']:
            clips = []
            for clip_data in group['clips']:
                clip_filename = process_clip(original_files[0], clip_data, clips_directory, uuid, group['group_id'])
                clip_data['filename'] = clip_filename  # Update the clip data with the actual filename
                clips.append(clip_filename)

            if group['merge_required']:
                merged_filename = os.path.join(clips_directory, group['final_filename'] or f'merged_output_{uuid}_{group["group_id"]}.mp4')
                if clips:
                    merged_clip = concatenate_videoclips([VideoFileClip(clip) for clip in clips])
                    merged_clip.write_videofile(merged_filename, codec='libx264', audio_codec='aac')
                    logging.info(f"Merged clips saved to {merged_filename}")

            # Move the merged file to the final serve directory if needed
            if group['merge_required']:
                final_filename = associated_task.get('final_downloaded_filename', f'final_output_{uuid}.mp4')
                final_filepath = os.path.join(final_serve_directory, final_filename)
                if os.path.exists(merged_filename):
                    os.rename(merged_filename, final_filepath)
                    logging.info(f"Final merged video saved to {final_filepath}")

def process_clip(video_file, clip_data, clips_directory, uuid, group_id):
    """Extracts and processes a single clip from the video file."""
    start_time = clip_data['start_time']
    end_time = clip_data['end_time']

    clip = VideoFileClip(video_file).subclip(start_time, end_time)

    clip_filename = os.path.join(clips_directory, f"clip_{uuid}_{group_id}_{clip_data['clip_id']}.mp4")
    clip.write_videofile(clip_filename, codec='libx264', audio_codec='aac')
    logging.info(f"Clip saved to {clip_filename}")

    return clip_filename

def merge_videos(video_files, output_file):
    if not video_files:
        logging.error("No video files to merge. Aborting merge.")
        return
    logging.info(f"Merging {len(video_files)} videos into {output_file}")

    clips = [VideoFileClip(video) for video in video_files]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
    logging.info(f"Saved merged video to {output_file}")
