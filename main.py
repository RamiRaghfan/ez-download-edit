import json
import logging
from pathlib import Path
from connection import connect_to_jdownloader, get_jd_device, disconnect_jdownloader
import downloader
import video_processor

logging.basicConfig(level=logging.DEBUG)

base_directory = Path("C:/Users/rami.raghfan/Downloads/ingest")
json_directory = Path(__file__).parent  # Root directory where Python files are
shared_directory = base_directory / "shared"
originals_directory = base_directory / "originals"
clips_directory = base_directory / "clips"
final_serve_directory = base_directory / "final_serve"

# Ensure necessary directories exist
originals_directory.mkdir(parents=True, exist_ok=True)
clips_directory.mkdir(parents=True, exist_ok=True)
final_serve_directory.mkdir(parents=True, exist_ok=True)

try:
    connect_to_jdownloader()  # Now handled by connection.py
except Exception as e:
    logging.error(f"Failed to connect to JDownloader API: {e}")
    exit(1)

try:
    jd_device = get_jd_device()
    jd_device.linkgrabber.remove_links(link_ids=[], package_ids=[])
except Exception as e:
    logging.error(f"Failed to retrieve JDownloader device: {e}")
    exit(1)

json_file = None
for json_file in json_directory.glob("*.json"):
    logging.info(f"Processing JSON file: {json_file}")

    with open(json_file, 'r') as f:
        ticket_data = json.load(f)

    links = ticket_data["package"]["links"]
    global_merge_all = ticket_data["package"].get("globalMergeAll", False)
    global_merged_title = ticket_data["package"].get("globalMergedTitle", "default_title")

    ticket_id = json_file.stem

    ticket_originals_directory = originals_directory / ticket_id
    ticket_clips_directory = clips_directory / ticket_id
    ticket_final_serve_directory = final_serve_directory / ticket_id

    ticket_originals_directory.mkdir(parents=True, exist_ok=True)
    ticket_clips_directory.mkdir(parents=True, exist_ok=True)
    ticket_final_serve_directory.mkdir(parents=True, exist_ok=True)

    videos_dict = {}

    connect_to_jdownloader()

    for idx, link in enumerate(links):
        print("IM ENTERING OOOOOOOOOOOOOOOOOOO")
        downloader.process_task(jd_device, link, idx, ticket_originals_directory, videos_dict)
        print("STILL INSIDE LOOOP HIIIIIIIIIIIIIIIII")

    disconnect_jdownloader()

    print("Now im OUTSIDE HAHAHAHAHAHAHA")

    video_processor.process_videos(
        videos_dict,
        ticket_originals_directory,
        ticket_clips_directory,
        ticket_final_serve_directory,
        ticket_id,
        global_merge_all, global_merged_title)

    logging.info(f"Completed processing for {json_file}")

