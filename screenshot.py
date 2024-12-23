import asyncio
import argparse
from pyppeteer import launch

async def take_screenshot(url, output_file):
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto(url)
    await page.screenshot({'path': output_file, 'fullPage': True})
    await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take a screenshot of a webpage.")
    parser.add_argument("url", type=str, help="The URL of the webpage to screenshot.")
    parser.add_argument("--output", type=str, default="screenshot.png", help="Output file name (default: screenshot.png).")
    args = parser.parse_args()

    asyncio.run(take_screenshot(args.url, args.output))