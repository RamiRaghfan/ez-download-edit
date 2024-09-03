import json
import logging
from pathlib import Path
from connection import connect_to_jdownloader, get_jd_device
import downloader
import video_processor

logging.basicConfig(level=logging.INFO)

# Credentials and device information
email = "rami.raghfan@gmail.com"
password = "!@#QWE123qwe"
device_name = "JDownloader@RAMI"

# Define the base directory for storing downloaded and processed files
base_directory = Path("C:/Users/rami.raghfan/Downloads/ingest")
shared_directory = base_directory / "shared"
ticket_directory = shared_directory / "ticket_directory"
ticket_directory.mkdir(parents=True, exist_ok=True)

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

uuid_mapping = {}

# Process each task in the ticket
for idx, task in enumerate(ticket_data["Tasks"]):
    # Create a directory for each task within the ticket directory
    task_directory = ticket_directory / f"task_{idx + 1}"
    task_directory.mkdir(parents=True, exist_ok=True)

    downloader.process_task(jd_device, task, idx, task_directory, uuid_mapping, originals_directory)

api.disconnect()
logging.info("Disconnected from JDownloader API.")

logging.info(f"UUID Mapping: {json.dumps(uuid_mapping, indent=2)}")

video_processor.process_videos(uuid_mapping, originals_directory, clips_directory, final_serve_directory)
