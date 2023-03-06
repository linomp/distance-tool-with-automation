from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://www.google.com/maps/@41.29085,12.71216,6z?hl=en")
    page.click("form[action*='consent.google.com'] button")

    page.fill("input[aria-label='Search Google Maps']", "palermo")
    page.click("button[aria-label='Directions']")
    page.fill("input[aria-label='Choose starting point, or click on the map...']", "torino")
    page.click("img[aria-label='Driving']")

    page.wait_for_selector("div#section-directions-trip-0")
    distance = page.inner_text("div#section-directions-trip-0")
    distance = [line for line in distance.splitlines() if "km" in line][0]

    print(distance)
    browser.close()
