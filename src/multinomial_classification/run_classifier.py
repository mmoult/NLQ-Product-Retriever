import pickle
from sklearn.feature_extraction.text import CountVectorizer
import src.multinomial_classification.clean_query as clean_query
import numpy as np

class Classifier():
    def __init__(self):
        from pathlib import Path
        # Load saved classifier
        with open(Path(__file__).parent / 'classifier.pkl', 'rb') as fid:
            self.classifier = pickle.load(fid)
        # create a new bag of words for the classification
        corpus = []
        # cleaned queries from the query dataset we had
        with open(Path(__file__).parent / 'vectorizer.pkl','rb') as vectorizer:
            self.vectorizer = pickle.load(vectorizer)

    def classify(self, query_list):
        # A sample test query list need to be classified
        # clean the query
        c = clean_query.clean()
        query_list = [c.clean_text(q) for q in query_list]
        #print(query_list)
        # add the test query to be classified to the whole list, and use the entire list to creat a bag of words
        # use the bag of word to convert the test query to word vector
        x_test = self.vectorizer.transform(query_list).toarray()
        #print(x_test.shape)
        # use the model to do the prediction for test query
        predict = self.classifier.predict(x_test)
        return predict


if __name__=="__main__":
    '''
    import nltk
    nltk.download('stopwords')
    '''
    c = Classifier()

    query_list = ["house in Melbourne Australia with 5 bedrooms",'senior data engineer in utah','apartment in Provo','house in Australia with 2 bathrooms', 'toyota black car in excellent condition cheapest']
    print(c.classify(query_list))