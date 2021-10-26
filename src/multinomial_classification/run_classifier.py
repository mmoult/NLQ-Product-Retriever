import pickle
from sklearn.feature_extraction.text import CountVectorizer
import clean_query
import numpy as np

class classifier():
    def __init__(self):
        # Load saved classifier
        with open('classifier.pkl', 'rb') as fid:
            self.classifier = pickle.load(fid)
        # create a new bag of words for the classification
        corpus = []
        # cleaned queries from the query dataset we had
        with open('corpus.txt') as file:
            corpus = file.readlines()
            self.corpus = [corpus.rstrip() for corpus in corpus]

    def classify(self, query_list):
        # A sample test query list need to be classified
        # clean the query
        c = clean_query.clean()
        query_list = [c.clean_text(q) for q in query_list]

        # add the test query to be classified to the whole list, and use the entire list to creat a bag of words
        self.corpus.extend(query_list)
        # use the bag of word to convert the test query to word vector
        cv = CountVectorizer()
        x = cv.fit_transform(self.corpus).toarray()
        x_test = x[-len(query_list):]

        # use the model to do the prediction for test query
        predict = self.classifier.predict(x_test)
        print(predict)

if __name__=="__main__":
    c = classifier()
    query_list = ["How many is new Honda Accord?", "Where to buy a good silver ring"]
    c.classify(query_list)