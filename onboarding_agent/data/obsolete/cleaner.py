import re
import time
from datetime import datetime

import pandas as pd
import unicodedata
from tqdm import tqdm


def iso_8601_to_timestamp(iso):
    dt = datetime.fromisoformat(iso)
    timestamp = dt.timestamp()
    return timestamp


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

def clean():

    file_path = r"../dump/banking_300k.csv"
    cleaned_file_path = r"dump/banking_300k_cleaned.csv"

    df = pd.read_csv(file_path, chunksize=100000)
    # Get the most recent message per conversation
    df = df.loc[df.groupby('conversation_id')['date_time'].idxmax()]

    # Sort by most recent first
    df = df.sort_values('date_time', ascending=False).reset_index(drop=True)

    first_chunk = True

    for chunk in tqdm(df, desc="Cleaning chunk rows"):
        # 1) removing duplicates having the same id and text conversation
        chunk = chunk.drop_duplicates(subset=['conversation_id', "text"])



        # 2) removing nan cuz it is causing errors for processing and useless for our case
        chunk = chunk.dropna()
        # 3) applying the cleaning function on the text column
        """Removing the cleaning function reduces the time from 4:19 to 01:12"""
        # chunk['text'] = chunk['text'].apply(clean_conversation_text)  #
        # 4) convert to timestamp
        chunk['date_time'] = chunk['date_time'].apply(iso_8601_to_timestamp)

        if first_chunk:
            chunk.to_csv(cleaned_file_path, index=False, mode='w', header=True)
            first_chunk = False
        else:
            chunk.to_csv(cleaned_file_path, index=False, mode='a', header=False)

if __name__ == "__main__":
    clean()
    # l = ["hello", "يَذْهَبُ مُحَمَّدٌ لِلْمَدْرَسَةِ كُلَّ صَبَاحٍ", "hello", "اللَّهمَّ اغْفِرْ لنَا ولوالدِينَا",
    #      "Crème Brûlée, café, àéêöhello"]
    #
    # print(process_cleaning(l))
