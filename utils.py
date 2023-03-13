import codecs
import os

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

load_dotenv()


# Source: https://stackoverflow.com/a/35038703/8522453
def unescaped_str(arg_str) -> str:
    return codecs.decode(str(arg_str), 'unicode_escape')


def parse_line(line: str, delimiter: str) -> (str, str):
    line = line.replace("\n", "")
    origin, destination = line.split(delimiter)
    origin = origin.replace('"', '')
    destination = destination.replace('"', '')
    return origin, destination


def setup_output_file(filename: str, delimiter: str):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(f"origin{delimiter}destination{delimiter}driving_distance_km" + "\n")


def write_to_output_file(filename: str, delimiter: str, origin: str, destination: str, distance: str):
    # if "ERROR" in distance:
    #     write_to_error_file(filename=filename, delimiter=delimiter, origin=origin, destination=destination)

    with open(filename, "a") as o:
        o.write(f"{origin}{delimiter}{destination}{delimiter}{distance}\n")


def write_to_error_file(filename: str, delimiter: str, origin: str, destination: str):
    filename = filename.replace(".csv", "_failures.csv")
    with open(filename, "a") as o:
        o.write(f"{origin}{delimiter}{destination}\n")


def send_telegram_notification(filename: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if token is None or chat_id is None:
        return

    message = f"Finished processing: {filename.split('/')[-1]}"

    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    session.get(url)
