import re
import unicodedata


def clean_conversation_text(text):
    # normalizing with NFKC for special characters and accents
    text = unicodedata.normalize('NFD', text)

    text = "".join(
        char for char in text
        if unicodedata.category(char) != 'Mn'
        or ('\u0600' <= char <= '\u06FF')
    )

    # removing tashkeel
    tashkeel_pattern = re.compile(r'[\u064B-\u0652\u0640]')
    text = re.sub(tashkeel_pattern, '', text)

    text = unicodedata.normalize('NFC', text)

    # collapse white space and new lines
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n+', '\n', text)

    return text.strip()

def process_cleaning(messages):
    # cleaning every message
    cleaned_messages = [clean_conversation_text(m) for m in messages]
    # simple deduplication
    unique_messages = list(set(cleaned_messages))
    return unique_messages


l = ["hello", "يَذْهَبُ مُحَمَّدٌ لِلْمَدْرَسَةِ كُلَّ صَبَاحٍ", "hello", "اللَّهمَّ اغْفِرْ لنَا ولوالدِينَا", "Crème Brûlée, café, àéêöhello"]

print(process_cleaning(l))