import os
import time

from playwright.sync_api import sync_playwright


def parse_line(line, delimiter):
    line = line.replace("\n", "")
    source, destination = line.split(delimiter)
    source = source.replace('"', '')
    destination = destination.replace('"', '')
    return source, destination


def setup_output_file(file, delimiter):
    if not os.path.exists(file):
        with open(file, "w") as f:
            f.write(f"source{delimiter}destination{delimiter}driving_distance_km" + "\n")


def write_to_output_file(file, delimiter, source, destination, distance):
    with open(file, "a") as o:
        # Replace commas with semicolons to avoid problems with CSV
        source = source.replace(",", ";")
        destination = destination.replace(",", ";")
        o.write(f"{source}{delimiter}{destination}{delimiter}{distance}\n")


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

                source, destination = parse_line(line=line, delimiter=input_delimiter)

                print(f"Searching distance from {{{source}}} to {{{destination}}}...")

                try:
                    page.wait_for_selector("div#directions-searchbox-0 input")
                    page.fill("div#directions-searchbox-0 input", source)

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

                write_to_output_file(file=output_file, delimiter=output_delimiter, source=source,
                                     destination=destination, distance=distance)

                # sleep to not overload google maps
                time.sleep(seconds_to_sleep_between_searches)
                page.goto(google_maps_start_url)

            browser.close()


if __name__ == "__main__":
    get_distances_line_by_line(
        input_file="input.txt",
        input_delimiter="\t",
        output_file="output.csv",
        output_delimiter=",",
        google_maps_start_url="https://www.google.com/maps/dir///@41.1905507,3.395374,5z/data=!4m2!4m1!3e0?hl=en",
        seconds_to_sleep_between_searches=1,
        headless=True
    )
