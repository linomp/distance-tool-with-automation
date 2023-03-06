import argparse
import codecs
import os
import time

from playwright.sync_api import sync_playwright


# Source: https://stackoverflow.com/a/35038703/8522453
def unescaped_str(arg_str):
    return codecs.decode(str(arg_str), 'unicode_escape')


def parse_line(line, delimiter):
    line = line.replace("\n", "")
    origin, destination = line.split(delimiter)
    origin = origin.replace('"', '')
    destination = destination.replace('"', '')
    return origin, destination


def setup_output_file(file, delimiter):
    if not os.path.exists(file):
        with open(file, "w") as f:
            f.write(f"origin{delimiter}destination{delimiter}driving_distance_km" + "\n")


def write_to_output_file(file, delimiter, origin, destination, distance):
    with open(file, "a") as o:
        # Replace commas with semicolons to avoid problems with CSV
        origin = origin.replace(",", ";")
        destination = destination.replace(",", ";")
        o.write(f"{origin}{delimiter}{destination}{delimiter}{distance}\n")


def get_distances_line_by_line(input_file="input.txt",
                               input_delimiter="\t",
                               output_file="output.csv",
                               output_delimiter=",",
                               google_maps_start_url="https://www.google.com/maps/dir///@41.1905507,3.395374,5z/data=!4m2!4m1!3e0?hl=en",
                               seconds_to_sleep_between_searches=1,
                               headless=True):
    setup_output_file(file=output_file, delimiter=output_delimiter)

    with open(input_file, "r") as f:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            page.goto(google_maps_start_url)
            page.click("form[action*='consent.google.com'] button")

            # Read input file line by line
            while True:
                line = f.readline()
                if not line:
                    break

                origin, destination = parse_line(line=line, delimiter=input_delimiter)

                print(f"Searching distance from {{{origin}}} to {{{destination}}}...")

                try:
                    page.wait_for_selector("div#directions-searchbox-0 input")
                    page.fill("div#directions-searchbox-0 input", origin)

                    page.wait_for_selector("div#directions-searchbox-1 input")
                    page.fill("div#directions-searchbox-1 input", destination)

                    page.click("img[aria-label='Driving']")
                    page.click("div#directions-searchbox-1 input")
                    page.press("div#directions-searchbox-1 input", "Enter")

                    page.wait_for_selector("div#section-directions-trip-0", timeout=60000)

                    distance = page.inner_text("div#section-directions-trip-0")
                    distance = [line for line in distance.splitlines() if "km" in line][0]
                    distance = distance.replace(",", "").replace("km", "").strip()
                except:
                    distance = "ERROR"

                print(f"Result: {distance} km")

                write_to_output_file(file=output_file, delimiter=output_delimiter, origin=origin,
                                     destination=destination, distance=distance)

                # sleep to not overload google maps
                time.sleep(seconds_to_sleep_between_searches)
                page.goto(google_maps_start_url)

            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input file", type=str, default="input.txt")
    parser.add_argument("-d", "--delimiter", help="Input file delimiter", type=unescaped_str, default="\t")
    parser.add_argument("-o", "--output", help="Output file", type=str, default="output.csv")
    parser.add_argument("-od", "--output-delimiter", help="Output file delimiter", type=str, default=",")
    parser.add_argument("-s", "--seconds-to-sleep-between-searches", help="Seconds to sleep between searches", type=int,
                        default=1)

    args = parser.parse_args()

    get_distances_line_by_line(
        input_file=args.input,
        input_delimiter=args.delimiter,
        output_file=args.output,
        output_delimiter=args.output_delimiter,
        google_maps_start_url="https://www.google.com/maps/dir///@41.1905507,3.395374,5z/data=!4m2!4m1!3e0?hl=en",
        seconds_to_sleep_between_searches=args.seconds_to_sleep_between_searches,
        headless=True
    )
