import json
import logging
from pathlib import Path
from connection import connect_to_jdownloader, get_jd_device
import downloader
import video_processor

logging.basicConfig(level=logging.DEBUG)

# Credentials and device information
email = "xxx"
password = "xxx"
device_name = "xxx"

base_directory = Path("C:/Users/rami.raghfan/Downloads/ingest")
shared_directory = base_directory / "shared"

originals_directory = base_directory / "originals"
clips_directory = base_directory / "clips"
final_serve_directory = base_directory / "final_serve"

originals_directory.mkdir(parents=True, exist_ok=True)
clips_directory.mkdir(parents=True, exist_ok=True)
final_serve_directory.mkdir(parents=True, exist_ok=True)

ticket_file = Path("ticket.json")
with open(ticket_file, 'r') as f:
    ticket_data = json.load(f)

# We now retrieve `links` from the `package` key instead of `Tasks`
links = ticket_data["package"]["links"]
global_merge_all = ticket_data["package"].get("globalMergeAll", False)
global_merged_title = ticket_data["package"].get("globalMergedTitle", "")

ticket_id = ticket_file.stem  # Use the JSON filename as the ticket ID
ticket_originals_directory = originals_directory / ticket_id
ticket_originals_directory.mkdir(parents=True, exist_ok=True)

try:
    api = connect_to_jdownloader(email, password)
except Exception as e:
    logging.error(f"Failed to connect to JDownloader API: {e}")
    exit(1)

try:
    jd_device = get_jd_device(api, device_name)
except Exception as e:
    logging.error(f"Failed to retrieve JDownloader device: {e}")
    exit(1)

videos_dict = {}

# Loop over links in the updated structure
jd_device.linkgrabber.remove_links(link_ids=[], package_ids=[])

for idx, link in enumerate(links):
    downloader.process_task(jd_device, link, idx, ticket_originals_directory, videos_dict)

api.disconnect()
logging.info("Disconnected from JDownloader API.")

logging.info(f"Videos Dictionary: {json.dumps(videos_dict, indent=2)}")

#video_processor.process_videos(videos_dict, originals_directory, clips_directory, final_serve_directory, global_merge_all, global_merged_title)
