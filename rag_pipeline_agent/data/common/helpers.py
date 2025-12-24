from pathlib import Path
from urllib.parse import urlparse

def create_and_get_website_dir_if_not_exist(website: str):

    if not website.startswith("http"):
        raise ValueError(f"Invalid URL: it must begin with 'http://' or 'https://'")

    # getting the website url
    url_parsed_result = urlparse(website)
    url = url_parsed_result.netloc

    if not url:
        raise ValueError(f"Please make sure that you entered a valid url. Extracted url: '{url}' from '{website}'")

    try:
        # getting the path (first item only) to create multiple scrapped dir for a website
        path = url_parsed_result.path
        if path:
            path = path.split("/")[1]


        # getting the website name
        split_index = 0 if "www." not in url else 1
        dir_website_name = url.split(".")[split_index]

        # create scrapped dir if not already there
        parent = Path(__file__).parent / "scrapped"
        parent.mkdir(parents=True, exist_ok=True)


        # create website and path dir if not already there
        scrapped_website_dir = parent / dir_website_name
        scrapped_website_dir.mkdir(parents=True, exist_ok=True)

        # create path if not already there
        website_path = None
        if path:
            website_path = scrapped_website_dir / path
            website_path.mkdir(parents=True, exist_ok=True)

        file_path =  website_path if website_path else scrapped_website_dir
        return dir_website_name, path, file_path
    except IndexError as e:
        IndexError(f"Please make sure that you entered a valid url: {e}")


if __name__ == "__main__":
    print(create_and_get_website_dir_if_not_exist("https/ds/d/d/"))