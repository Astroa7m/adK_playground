import asyncio
import os

from dotenv import load_dotenv
from firecrawl import AsyncFirecrawl, Firecrawl

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

crawler = AsyncFirecrawl(api_key=api_key)

docs = None

async def crawl_site(url: str):
    global docs

    if not url.startswith("http"):
        raise ValueError(f"Invalid URL: it must begin with 'http://' or 'https://'")

    if not api_key:
        raise KeyError("api key not found in env")

    try:
        docs = await crawler.crawl(
            url=url,
            scrape_options={
                "formats": [
                    'markdown'
                ]
            },
            limit=10,
            crawl_entire_domain=False
        )
    except Exception as e:
        raise RuntimeError(f"Crawl failed unexpectedly: {e}")

# as long as you see some output, you wouldn't give up waiting
async def monitor():
    waited_time = 0
    while docs is None:
        if waited_time < 30:
            print("Please wait")
        elif waited_time < 60:
            print("Please wait a little longer")
        elif waited_time < 120:
            print("Hang-on, we are almost there")
        else:
            print("Let's pray we finish soon")
        waited_time += 10
        await asyncio.sleep(10)
    else:
        print("Total wait time", waited_time)
        print("Job Completed we have successfully scraped the website")


async def main(url: str):
    try:
        # If crawl_site raises an exception, gather will propagate it immediately
        # and stop the monitor automatically.
        await asyncio.gather(crawl_site(url), monitor())
        return docs.data
    except Exception as e:
        print(f"Crawl Task Failed: {e}")
        raise

if "__main__" == __name__:
    print(asyncio.run(main("www.omantel.com")))


