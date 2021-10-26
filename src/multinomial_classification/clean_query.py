import pandas as pd
import nltk
from nltk.stem import PorterStemmer
import textwrap
from spacy.lang.en import STOP_WORDS
# from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
# nltk.download('stopwords')
porter = PorterStemmer()
stops = list(set(stopwords.words('english') + list(set(STOP_WORDS))))
import string
from nltk import sent_tokenize
from nltk.tokenize import word_tokenize
import re
porter = PorterStemmer()
exclude = set(",.:;'\"-?!/")

# nltk.download('punkt')

class clean():
    def __init__(self):
        pass
    def clean_text(self,text):
        text = text.replace('\\n',' ').strip()
        words = text.split()
        cleand_words = []
        for word in words:
            if not any (c.isdigit() for c in word):
                word = "".join([(ch if ch not in exclude else " ") for ch in word]).lower()
                cleand_words.append(word)

        text = ' '.join(cleand_words)
        tokens = word_tokenize(text)
        cleaned_text = []
        for word in tokens:
            if word.isalpha() and not (word in stops):
                word = porter.stem(word)
                cleaned_text.append(word)
        return ' '.join(cleaned_text)

# example
# if __name__ == "__main__":
#     c = clean()
#     print(c.clean_text('How much is Honda Accord'))
