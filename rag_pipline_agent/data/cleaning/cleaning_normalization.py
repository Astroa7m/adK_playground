import re

from unidecode import unidecode


def normalize_links(data: str):
    """
    Converting '[Read more](https://site.com/page1)' to 'Read more https://site.com/page1'
    Works for links, clickables, images
    """
    # Pattern: [text](url)
    # \!? - optional exclamation mark to conver both links and images
    # \[      - literal opening bracket
    # ([^\]]*) - capture group 1: any chars except ']' (the link text)
    # \]      - literal closing bracket
    # \(      - literal opening parenthesis
    # ([^)]+) - capture group 2: any chars except ')' (the URL)
    # \)      - literal closing parenthesis

    pattern = r'\!?\[([^\]]*)\]\(([^)]+)\)'

    def replacer(match):
        text = match.group(1).strip()
        url = match.group(2).strip()
        # If text is empty, just use the URL
        if text:
            return f'{text} {url}'
        return url

    result = re.sub(pattern, replacer, data)

    return result


def remove_image_alt_link(data: str):
    """Removing '![alt](https://site.com/image.jpg)' completely """
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    result = re.sub(pattern, "", data)
    return result


def fix_multiple_newlines(data: str):
    """Removing multiple \n or enter symbols to single one"""
    # \n{2,} means: 2 or more consecutive newlines
    # handle literal newline characters
    result = re.sub(r'\n{2,}', '\n', data)

    # handle escaped newlines in text (like "\\n")
    result = re.sub(r'(\\n){2,}', r'\\n', result)

    # handle mixed cases where there might be actual newlines and spaces
    result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)

    return result


def standardize_encoding(data: str):
    """Converting fancy encoding to ASCI standard"""
    # this removes Arabic as well
    return unidecode(data)


def deduplicate(data: str):
    """Removing duplication"""

    def deduplicate_single_line(line):
        # just arbitray, any sentence/line under 20 is assuming doesn't have duplicates
        LIMIT = 20

        line = line.strip()

        if len(line) < LIMIT:
            return line

        """
        ^: begin of string
        (...): matches group, whatever within the parenthesis or more chars
        .: matches any character, except new lines
        .{10}: exactly match 10
        .{10,}: match 10 or more
        .{10,20}: match between 10 and 20
        \1+: captures the repeated group once or more
        $: end of string
        """
        pattern = rf"^(.{{{LIMIT},}}?)\1+$"

        match = re.match(pattern, line)

        if match:
            return match.group(1)  # return the first duplicate only

        # no match return the line
        return line

    lines = data.split("\n")

    # we start by removing duplicates on the same line
    cleaned_lines = [deduplicate_single_line(line) for line in lines]
    # better than a result list because of O(n) lookups
    # better than a result list and a set combo (less space complexity)
    # can be a dict like this: seen[cleaned_line] = None, but the following is one more straightforward
    # but this is even better
    unique = dict.fromkeys(cleaned_lines).keys()
    return "\n".join(unique)


def clean_all(data, remove_images=False):
    normalized_link = normalize_links(data)

    if remove_images:
        normalized_link = remove_image_alt_link(normalized_link)

    lines_fixed = fix_multiple_newlines(normalized_link)

    standardized = standardize_encoding(lines_fixed)

    final_cleaned = deduplicate(standardized)

    return final_cleaned


if __name__ == "__main__":
    with (open("../crawling/scraped_output_example.md", encoding="utf-8") as in_f,
          open("../crawling/scraped_output_example_cleaned.md", mode='w', encoding="utf-8") as out_f):
        raw = in_f.read()
        init_len = len(raw)
        cleaned = clean_all(raw)
        out_f.write(cleaned)
        final_len = len(cleaned)
        print("Cleand Saved to file: ../crawling/scraped_output_example_cleaned.md")

        print(f"Length before: {init_len}")
        print(f"Length After: {final_len}")
