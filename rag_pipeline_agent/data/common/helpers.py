import json
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

        file_path = website_path if website_path else scrapped_website_dir
        return dir_website_name, path, file_path
    except IndexError as e:
        IndexError(f"Please make sure that you entered a valid url: {e}")


def clean_up(path_str: str):
    path = Path(path_str)
    # just for debugging purposes and to avoid deletion
    confi_file = Path(__file__).parent / "config.json"
    with open(confi_file) as f:
        allow_deletion = json.load(f)['allow_deletion']

    if allow_deletion:
        # listing child if found
        for child in path.rglob("*"):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                clean_up(str(child))
        # if no children and it is a dir remove
        if path.is_dir():
            path.rmdir()
        # if is a file
        if path.is_file():
            path.unlink()

if __name__ == "__main__":
    # print(create_and_get_website_dir_if_not_exist("https/ds/d/d/"))
    # clean_up(Path(r"C:\Users\ahmed\PycharmProjects\tryingADK\rag_pipeline_agent\data\common\scrapped"))
    pass