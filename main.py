import argparse
import codecs
import os
import time

from playwright.sync_api import sync_playwright, Page


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


def write_to_output_file(filename, delimiter, origin, destination, distance):
    with open(filename, "a") as o:
        # Replace commas with semicolons to avoid problems with CSV
        origin = origin.replace(",", ";")
        destination = destination.replace(",", ";")
        o.write(f"{origin}{delimiter}{destination}{delimiter}{distance}\n")


def get_distance_from_google_maps(origin: str, destination: str, page: Page,
                                  google_maps_query_timeout: int) -> str:
    try:
        page.wait_for_selector("div#directions-searchbox-0 input")
        page.fill("div#directions-searchbox-0 input", origin)

        page.wait_for_selector("div#directions-searchbox-1 input")
        page.fill("div#directions-searchbox-1 input", destination)

        page.click("img[aria-label='Driving']")
        page.click("div#directions-searchbox-1 input")
        page.press("div#directions-searchbox-1 input", "Enter")

        page.wait_for_selector("div#section-directions-trip-0", timeout=google_maps_query_timeout)

        distance = page.inner_text("div#section-directions-trip-0")
        distance = [line for line in distance.splitlines() if "km" in line][0]
        distance = distance.replace(",", "").replace("km", "").strip()
    except:
        distance = "ERROR"

    return distance


def start_processing_loop(input_file="data/input.txt",
                          input_delimiter="\t",
                          output_file="data/output.csv",
                          output_delimiter=",",
                          google_maps_start_url="https://www.google.com/maps/dir///@41.1905507,3.395374,5z/data=!4m2!4m1!3e0?hl=en",
                          seconds_to_sleep_between_searches=1,
                          google_maps_query_timeout=60000,
                          headless=True):
    setup_output_file(filename=output_file, delimiter=output_delimiter)

    with open(input_file, "r") as f:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless, slow_mo=250)
            page = browser.new_page()

            page.goto(google_maps_start_url)
            try:
                page.wait_for_selector("form[action*='consent.google.com'] button", timeout=google_maps_query_timeout)
                page.click("form[action*='consent.google.com'] button")
            except:
                if page.query_selector("div#directions-searchbox-0 input") is None:
                    raise Exception("Google Maps did not load correctly")

            while True:
                line = f.readline()
                if not line:
                    break

                origin, destination = parse_line(line=line, delimiter=input_delimiter)

                print(f"Searching distance from {{{origin}}} to {{{destination}}}...")

                distance = get_distance_from_google_maps(origin=origin, destination=destination, page=page,
                                                         google_maps_query_timeout=google_maps_query_timeout)

                print(f"Result: {distance} km")

                write_to_output_file(filename=output_file, delimiter=output_delimiter, origin=origin,
                                     destination=destination, distance=distance)

                # Small pause to not overload google maps
                time.sleep(seconds_to_sleep_between_searches)
                page.goto(google_maps_start_url)

            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input filename", type=str, default="data/input.txt")
    parser.add_argument("-d", "--delimiter", help="Input filename delimiter", type=unescaped_str, default="\t")
    parser.add_argument("-o", "--output", help="Output filename", type=str, default="data/output.csv")
    parser.add_argument("-od", "--output-delimiter", help="Output filename delimiter", type=str, default=",")
    parser.add_argument("-s", "--seconds-to-sleep-between-searches", help="Seconds to sleep between searches", type=int,
                        default=1)
    parser.add_argument("-t", "--google-maps-query-timeout", help="Google maps query timeout", type=int, default=60000)
    parser.add_argument("-hl", "--headless", help="Headless mode", type=int, default=1)

    args = parser.parse_args()

    start_processing_loop(
        input_file=args.input,
        input_delimiter=args.delimiter,
        output_file=args.output,
        output_delimiter=args.output_delimiter,
        seconds_to_sleep_between_searches=args.seconds_to_sleep_between_searches,
        google_maps_query_timeout=args.google_maps_query_timeout,
        headless=bool(args.headless)
    )
