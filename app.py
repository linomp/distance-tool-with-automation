import argparse
import asyncio

from playwright.async_api import async_playwright, Page

from utils import setup_output_file, parse_line, write_to_output_file, unescaped_str, send_telegram_notification


async def handle_google_cookies(page: Page, timeout: int):
    try:
        await page.wait_for_selector("form[action*='consent.google.com'] button",
                                     timeout=timeout)
        await page.click("form[action*='consent.google.com'] button")
    except:
        if await page.query_selector("div#directions-searchbox-0 input") is None:
            raise Exception("Google Maps did not load correctly")


async def get_distance_from_google_maps(page: Page, origin: str, destination: str,
                                        timeout: int) -> str:
    try:
        await page.wait_for_selector("div#directions-searchbox-0 input")
        await page.fill("div#directions-searchbox-0 input", origin)

        await page.wait_for_selector("div#directions-searchbox-1 input")
        await page.fill("div#directions-searchbox-1 input", destination)

        await page.click("img[aria-label='Driving']")
        await page.click("div#directions-searchbox-1 input")
        await page.press("div#directions-searchbox-1 input", "Enter")

        await page.wait_for_selector("div#section-directions-trip-0", timeout=timeout)

        distance = await page.inner_text("div#section-directions-trip-0")
        distance = [line for line in distance.splitlines() if "km" in line][0]
        distance = distance.replace(",", "").replace("km", "").strip()
    except:
        distance = "ERROR"

    return distance


async def start_processing_loop(input_file="data/input.txt",
                                input_delimiter="\t",
                                output_file="data/output.csv",
                                output_delimiter="\t",
                                google_maps_start_url="https://www.google.com/maps/dir///@41.1905507,3.395374,5z/data=!4m2!4m1!3e0?hl=en",
                                seconds_to_sleep_between_searches=1,
                                google_maps_query_timeout=60000,
                                slow_mo=10,
                                headless=True):
    setup_output_file(filename=output_file, delimiter=output_delimiter)

    with open(input_file, "r") as f:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless, slow_mo=slow_mo)
            page = await browser.new_page()

            await page.goto(google_maps_start_url, timeout=google_maps_query_timeout)
            await handle_google_cookies(page=page, timeout=google_maps_query_timeout)

            while True:
                line = f.readline()
                if not line:
                    break

                origin, destination = parse_line(line=line, delimiter=input_delimiter)

                print(f"Searching distance from {{{origin}}} to {{{destination}}}...")

                distance = await get_distance_from_google_maps(page=page, origin=origin, destination=destination,
                                                               timeout=google_maps_query_timeout)

                print(f"Result: {distance} km")

                write_to_output_file(filename=output_file, delimiter=output_delimiter, origin=origin,
                                     destination=destination, distance=distance)

                # Small pause to not overload google maps
                await asyncio.sleep(seconds_to_sleep_between_searches)
                await page.goto(google_maps_start_url, timeout=google_maps_query_timeout)

            await browser.close()

    send_telegram_notification(input_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input filename", type=str, default="data/input.txt")
    parser.add_argument("-d", "--delimiter", help="Input filename delimiter", type=unescaped_str, default="\t")
    parser.add_argument("-o", "--output", help="Output filename", type=str, default="data/output.csv")
    parser.add_argument("-od", "--output-delimiter", help="Output filename delimiter", type=str, default="\t")
    parser.add_argument("-s", "--seconds-to-sleep-between-searches", help="Seconds to sleep between searches", type=int,
                        default=1)
    parser.add_argument("-sl", "--slow-mo", help="Playwright slow mo", type=int, default=250)
    parser.add_argument("-t", "--google-maps-query-timeout", help="Google maps query timeout", type=int, default=60000)
    parser.add_argument("-hl", "--headless", help="Headless mode", type=int, default=1)

    args = parser.parse_args()

    asyncio.run(start_processing_loop(
        input_file=args.input,
        input_delimiter=args.delimiter,
        output_file=args.output,
        output_delimiter=args.output_delimiter,
        slow_mo=args.slow_mo,
        seconds_to_sleep_between_searches=args.seconds_to_sleep_between_searches,
        google_maps_query_timeout=args.google_maps_query_timeout,
        headless=bool(args.headless)
    ))
