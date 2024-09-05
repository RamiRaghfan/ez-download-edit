import time
import logging
from myjdapi import Myjdapi

MAX_RETRIES = 3
RETRY_DELAY = 5


def retry(func):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                logging.error(f"Error: {e}. Retrying ({retries}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
        raise Exception(f"Failed after {MAX_RETRIES} retries.")

    return wrapper


@retry
def connect_to_jdownloader(email, password):
    api = Myjdapi()
    api.connect(email, password)
    logging.info("Connected successfully to JDownloader API.")
    return api


@retry
def get_jd_device(api, device_name):
    return api.get_device(device_name=device_name)
