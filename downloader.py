import time
import logging
import os

WAIT_TIME = 10  # seconds to wait after adding links to LinkGrabber
CHECK_INTERVAL = 10  # seconds to wait between download completion checks
TIMEOUT = 600  # seconds to wait before timing out on download completion

VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm')


def add_links_to_linkgrabber(jd_device, task, idx, task_directory):
    response = jd_device.linkgrabber.add_links(params=[{
        "autostart": False,
        "links": task["URL"],
        "packageName": f"task_{idx + 1}",
        "extractPassword": None,
        "priority": "DEFAULT",
        "downloadPassword": None,
        "destinationFolder": str(task_directory),
        "overwritePackagizerRules": False
    }])
    return response


def query_package_links(jd_device, package_id):
    return jd_device.linkgrabber.query_links(params=[{
        "packageUUIDs": [package_id],
        "startAt": 0,
        "maxResults": -1,
        "status": True,
        "url": True,
        "name": True,
        "bytesTotal": True,
        "host": True
    }])


def move_package_to_download_list(jd_device, package_id):
    jd_device.linkgrabber.move_to_downloadlist(link_ids=[], package_ids=[package_id])
    logging.info(f"Package {package_id} moved to download list.")


def wait_for_all_files(task_directory, expected_count, check_interval=CHECK_INTERVAL, timeout=TIMEOUT):
    """Wait for the expected number of files to appear in the task directory, checking periodically."""
    logging.info(f"Checking in task directory: {task_directory}")
    start_time = time.time()
    while time.time() - start_time < timeout:
        existing_files = [f for f in os.listdir(task_directory) if f.lower().endswith(VIDEO_EXTENSIONS)]
        logging.info(f"Checking files... {len(existing_files)} found in {task_directory}. Files: {existing_files}")
        if len(existing_files) >= expected_count:
            logging.info(f"Expected number of files found in {task_directory}: {existing_files}")
            return existing_files
        time.sleep(check_interval)
    logging.warning(f"Timed out waiting for files in {task_directory}.")
    return []


def process_task(jd_device, task, idx, task_directory, uuid_mapping):
    """Process each task to add links and download the videos."""
    try:
        # Add links to LinkGrabber
        link_response = add_links_to_linkgrabber(jd_device, task, idx, task_directory)
        logging.info(f"Task {idx + 1}: URL {task['URL']} added to LinkGrabber.")

        # Wait for the package to be processed
        time.sleep(WAIT_TIME)

        # Query the added package in LinkGrabber, filtering by package name
        package_name = f"task_{idx + 1}"
        package_query = jd_device.linkgrabber.query_packages(params=[{
            "packageUUIDs": [],
            "priority": True,
            "enabled": True,
            "bytesTotal": True,
            "childCount": True,
            "hosts": True,
            "startAt": 0,
            "maxResults": -1,
            "status": True,
            "saveTo": True,
            "eta": True,
            "running": True,
            "name": package_name  # Filter by package name specific to the task
        }])

        # Log the full package query response for debugging
        logging.info(f"Package Query Result: {package_query}")

        if not package_query:
            logging.warning(f"Task {idx + 1}: No package found with name {package_name}.")
            return

        for package in package_query:
            package_id = package['uuid']

            # Fetch the links associated with the package UUID
            links_query = query_package_links(jd_device, package_id)
            logging.info(f"Links Query Result for package {package_id}: {links_query}")

            # Filter video links
            video_links = [link for link in links_query if link['name'].lower().endswith(VIDEO_EXTENSIONS)]
            if video_links:
                move_package_to_download_list(jd_device, package_id)
                downloaded_files = wait_for_all_files(task_directory, len(video_links))

                # Update the UUID mapping
                uuid_mapping[package_id] = {
                    "link": task["URL"],
                    "title": package["name"],
                    "path": str(task_directory),
                    "associated_task": task,
                    "downloaded_files": downloaded_files
                }

            else:
                logging.info(f"Task {idx + 1}: Waiting to process package.. {package_id}.")
    except KeyError as e:
        logging.error(f"Task {idx + 1}: Failed to process URL {task['URL']} - KeyError: {e}")
    except Exception as e:
        logging.error(f"Task {idx + 1}: Failed to process URL {task['URL']} - {e}")
