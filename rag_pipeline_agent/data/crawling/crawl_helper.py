import asyncio
import os

from dotenv import load_dotenv
from firecrawl import AsyncFirecrawl, Firecrawl

from rag_pipeline_agent.data.common import SCRAPPED_EXT
from rag_pipeline_agent.data.common.helpers import create_and_get_website_dir_if_not_exist

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


async def async_scrape(file_path, website_url):
    try:
        # If crawl_site raises an exception, gather will propagate it immediately
        # and stop the monitor automatically.
        await asyncio.gather(crawl_site(website_url), monitor())
        # we are going to have a standard format for all scrapped data, all are going to be .md
        with open(file_path / SCRAPPED_EXT, "w", encoding="utf=8") as f:
            f.write(str(docs.data))
    except Exception as e:
        print(f"Crawl Task Failed: {e}")
        raise


def main(file_path, website_url):
    asyncio.run(async_scrape(file_path, website_url))

if "__main__" == __name__:
    print(asyncio.run(async_scrape("www.omantel.com")))


