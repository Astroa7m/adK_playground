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
    docs = await crawler.crawl(
        url=url,
        scrape_options={
            "formats": [
                'markdown'
            ]
        },
        limit=10,
        crawl_entire_domain=True
    )

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
    await asyncio.gather(crawl_site(url), monitor())

if "__main__" == __name__:
    asyncio.run(main("www.omantel.com"))
    print(docs)

