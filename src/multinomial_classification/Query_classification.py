#import os
#import string
#import numpy as np
#import matplotlib.pyplot as plt
from sklearn import model_selection
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score


if __name__ == "__main__":
    df = pd.read_csv('cleaned_queries.csv')
    df.head(1)
    df.dropna(inplace=True)
    corpus=df['cleaned_query'].tolist()
    with open('corpus.txt', 'w') as f:
        for item in corpus:
            f.write("%s\n" % item)
    # creating bag of words model
    cv = CountVectorizer()
    X = cv.fit_transform(corpus).toarray()
    Y = df['category'].tolist()
    X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X, Y, test_size=0.2, random_state=0)
    # fitting naive bayes to the training set

    classifier = MultinomialNB();
    classifier.fit(X_train, Y_train)

    # predicting test set results
    Y_pred = classifier.predict(X_test)

    # # making the confusion matrix
    # cm = confusion_matrix(Y_test, Y_pred)
    # print(cm)
    print(accuracy_score(Y_test, Y_pred))

    with open('classifier.pkl', 'wb') as fid:
        pickle.dump(classifier, fid)



