import logging
from moviepy.editor import concatenate_videoclips, VideoFileClip
from pathlib import Path  # Use pathlib for better path handling


def process_videos(videos_dict, originals_directory, clips_directory, final_serve_directory, ticket_id,
                   global_merge_all, global_merged_title):
    all_clips = []

    # Create a subdirectory for this ticket under final_serve_directory
    ticket_final_serve_directory = Path(final_serve_directory) / ticket_id  # Use Pathlib here
    ticket_final_serve_directory.mkdir(parents=True, exist_ok=True)  # Create the directory safely

    for video_file, video_data in videos_dict.items():
        logging.info(f"Processing video: {video_file}")
        associated_tasks = video_data["associated_tasks"]
        logging.info(f"Associated tasks: {associated_tasks}")

        print("PATH       " + str(video_file))
        original_file_path = Path(originals_directory) / video_file  # Pathlib for consistent path handling

        if not original_file_path.exists():
            logging.error(f"Video file not found: {original_file_path}")
            continue

        # Process each associated task
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
                        original_file_path.name  # Using pathlib 'name' instead of os.path.basename
                    )
                    clip_data['filename'] = clip_filename
                    clips.append(clip_filename)

                if group['merge_required']:
                    merged_filename = Path(
                        clips_directory) / f"{original_file_path.stem}_merged_{group['group_id']}.mp4"
                    if clips:
                        merged_clip = concatenate_videoclips([VideoFileClip(clip) for clip in clips])
                        merged_clip.write_videofile(str(merged_filename), codec='libx264',
                                                    audio_codec='aac')  # Convert to str
                        logging.info(f"Merged clips saved to {merged_filename}")

                        # Move the merged clip to the ticket-specific final serve directory
                        final_filename = f"{original_file_path.stem}_merged.mp4"
                        final_filepath = ticket_final_serve_directory / final_filename

                        if final_filepath.exists():
                            logging.info(f"File {final_filepath} already exists. Overwriting it.")
                            final_filepath.unlink()

                        merged_filename.rename(final_filepath)
                        logging.info(f"Final merged video saved to {final_filepath}")

                    if global_merge_all:
                        all_clips.append(VideoFileClip(str(merged_filename)))  # Convert to str

                else:
                    for clip in clips:
                        final_clip_path = ticket_final_serve_directory / Path(clip).name

                        if final_clip_path.exists():
                            logging.info(f"Clip {final_clip_path} already exists. Overwriting it.")
                            final_clip_path.unlink()

                        Path(clip).rename(final_clip_path)
                        logging.info(f"Clip moved to {final_clip_path}")

                    if global_merge_all:
                        all_clips.extend([VideoFileClip(clip) for clip in clips])

    if global_merge_all and all_clips:
        final_package_filename = ticket_final_serve_directory / f"{global_merged_title}.mp4"
        merged_package_clip = concatenate_videoclips(all_clips)
        merged_package_clip.write_videofile(str(final_package_filename), codec='libx264',
                                            audio_codec='aac')  # Convert to str
        logging.info(f"Global merged package saved to {final_package_filename}")


def process_clip(video_file, clip_data, clips_directory, task_idx, group_id, original_filename):
    """Extracts and processes a single clip from the video file."""
    start_time = clip_data['start_time']
    end_time = clip_data['end_time']

    clip = VideoFileClip(str(video_file)).subclip(start_time, end_time)  # Convert Path to str if needed

    # Generate the clip filename based on the original filename
    clip_filename = Path(
        clips_directory) / f"{Path(original_filename).stem}_clip_{task_idx}_{group_id}_{clip_data['clip_id']}.mp4"

    clip.write_videofile(str(clip_filename), codec='libx264', audio_codec='aac')  # Convert to str
    logging.info(f"Clip saved to {clip_filename}")

    # Close audio reader to avoid WinError
    if hasattr(clip.audio, 'reader'):
        clip.audio.reader.close_proc()

    return str(clip_filename)  # Return the filename as a string
