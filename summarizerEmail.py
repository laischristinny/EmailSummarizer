import pandas as pd
import spacy
from spacy.lang.pt.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from fetchEmails import fetch_and_save_emails_to_csv


def create_summary(text):
 
    stopwords = list(STOP_WORDS)

    nlp = spacy.load('pt_core_news_sm')

    doc = nlp(text)

    tokens = [token.text for token in doc]

    custom_punctuation = punctuation + '\n'  

    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in custom_punctuation:  
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_tokens = [sent for sent in doc.sents]

    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]

    select_length = int(len(sentence_tokens) * 0.3)

    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)

    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)

    return summary

def apply():
    fetch_and_save_emails_to_csv()
    df = pd.read_csv('emails_details.csv')
    df['summary'] = df['body'].apply(create_summary)
    df.to_csv('emails_resumidos.csv', index=False)
