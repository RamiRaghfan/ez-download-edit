import json
import logging
from pathlib import Path
from connection import connect_to_jdownloader, get_jd_device
import downloader
import video_processor

logging.basicConfig(level=logging.INFO)

# Credentials and device information
email = "xxx"
password = "xxx"
device_name = "xxx"

# Define the base directory for storing downloaded and processed files
base_directory = Path("C:/Users/rami.raghfan/Downloads/ingest")
shared_directory = base_directory / "shared"

# Intermediate directories
originals_directory = base_directory / "originals"
clips_directory = base_directory / "clips"
final_serve_directory = base_directory / "final_serve"

# Create the intermediate directories
originals_directory.mkdir(parents=True, exist_ok=True)
clips_directory.mkdir(parents=True, exist_ok=True)
final_serve_directory.mkdir(parents=True, exist_ok=True)

# Load ticket data from JSON file
ticket_file = Path("ticket.json")
with open(ticket_file, 'r') as f:
    ticket_data = json.load(f)

# Each ticket gets its own folder under originals
ticket_id = ticket_file.stem  # Use the JSON filename as the ticket ID
ticket_originals_directory = originals_directory / ticket_id
ticket_originals_directory.mkdir(parents=True, exist_ok=True)

# Attempt to connect to JDownloader
try:
    api = connect_to_jdownloader(email, password)
except Exception as e:
    logging.error(f"Failed to connect to JDownloader API: {e}")
    exit(1)

# Attempt to get the JDownloader device
try:
    jd_device = get_jd_device(api, device_name)
except Exception as e:
    logging.error(f"Failed to retrieve JDownloader device: {e}")
    exit(1)

# Initialize a dictionary to map videos to their tasks
videos_dict = {}

# Process each task in the ticket and populate the videos_dict
for idx, task in enumerate(ticket_data["Tasks"]):
    downloader.process_task(jd_device, task, idx, ticket_originals_directory, videos_dict)

api.disconnect()
logging.info("Disconnected from JDownloader API.")

logging.info(f"Videos Dictionary: {json.dumps(videos_dict, indent=2)}")

# Now process each video in the videos_dict
video_processor.process_videos(videos_dict, originals_directory, clips_directory, final_serve_directory)
