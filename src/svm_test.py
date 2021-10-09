
if __name__ == '__main__':
    # pip install sklearn
    from sklearn import datasets
    cancer = datasets.load_breast_cancer()
    
    print("Features:", cancer.feature_names)
    print("Labels:", cancer.target_names)
    print("Shape:", cancer.data.shape)
    print()
    print(cancer.data[0:5])
    print(cancer.target)
    
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(cancer.data, cancer.target, test_size=0.3)
    
    from sklearn import svm
    clf = svm.SVC(kernel='linear')
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    from sklearn import metrics
    print()
    print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
    print("Precision:", metrics.precision_score(y_test, y_pred))
    print("Recall:", metrics.recall_score(y_test, y_pred))
    
    # Test on data like so
    test = clf.predict([[1.799e+01, 1.038e+01, 1.228e+02, 1.001e+03, 1.184e-01, 2.776e-01, 3.001e-01,
                         1.471e-01, 2.419e-01, 7.871e-02, 1.095e+00, 9.053e-01, 8.589e+00, 1.534e+02,
                         6.399e-03, 4.904e-02, 5.373e-02, 1.587e-02, 3.003e-02, 6.193e-03, 2.538e+01,
                         1.733e+01, 1.846e+02, 2.019e+03, 1.622e-01, 6.656e-01, 7.119e-01, 2.654e-01,
                         4.601e-01, 1.189e-01]])
    # It must be a 2D array, so you can test on multiple points at once
    print(test)
    