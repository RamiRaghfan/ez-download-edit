import json
import logging
from pathlib import Path
from connection import connect_to_jdownloader, get_jd_device
import downloader

logging.basicConfig(level=logging.INFO)

# Credentials and device information
email = "xxx"
password = "xxx"
device_name = "xxx"

# Define the shared directory and ticket directory
shared_directory = Path("C:/Users/rami.raghfan/Downloads/ingest/shared")
ticket_directory = shared_directory / "ticket_directory"
ticket_directory.mkdir(parents=True, exist_ok=True)

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

    downloader.process_task(jd_device, task, idx, task_directory, uuid_mapping)

api.disconnect()
logging.info("Disconnected from JDownloader API.")

logging.info(f"UUID Mapping: {json.dumps(uuid_mapping, indent=2)}")
