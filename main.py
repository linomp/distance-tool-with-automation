import os
import time

from playwright.sync_api import sync_playwright

INPUT_FILE = "input.txt"
INPUT_DELIMITER = "\t"
OUTPUT_FILE = "output.csv"
OUTPUT_DELIMITER = ","
GOOGLE_MAPS_START_URL = "https://www.google.com/maps/dir///@41.1905507,3.395374,5z/data=!4m2!4m1!3e0?hl=en"
SECONDS_TO_SLEEP_BETWEEN_SEARCHES = 1

if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"source{OUTPUT_DELIMITER}destination{OUTPUT_DELIMITER}driving_distance_km"+"\n")

with open(INPUT_FILE, "r") as f:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(GOOGLE_MAPS_START_URL)
        page.click("form[action*='consent.google.com'] button")

        # Read input file line by line
        while True:
            line = f.readline()
            if not line:
                break

            line = line[:-1]
            source, destination = line.split(INPUT_DELIMITER)
            source = source.replace('"', '')
            destination = destination.replace('"', '')

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

            # Append result to output file
            with open(OUTPUT_FILE, "a") as o:
                source = source.replace(",", ";")
                destination = destination.replace(",", ";")
                o.write(f"{source}{OUTPUT_DELIMITER}{destination}{OUTPUT_DELIMITER}{distance}\n")

            # sleep to not overload google maps
            time.sleep(SECONDS_TO_SLEEP_BETWEEN_SEARCHES)
            page.goto(GOOGLE_MAPS_START_URL)

        browser.close()
