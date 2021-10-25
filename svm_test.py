
def loadData(fileName):
    class Dataset:
        def __init__(self, dataMass:[[int]]):
            # Here we are going to separate the data into the features and the target.
            # In all of our tagging files, the target is the first value, and the features are thereafter
            self.data = []
            self.target = []
            for line in dataMass:
                self.target.append(line[0])
                self.data.append(line[1:])
    
    from pathlib import Path
    file = open(str(Path(__file__).parent) + "/" + fileName)
    allLines = file.read()
    lines = allLines.split('\n')
    data = []
    for line in lines:
        if line and line[0] != '#':
            vals = line.split(',')
            bitVals = []
            for val in vals:
                bit = int(val)
                bitVals.append(bit)
            data.append(bitVals)
    file.close()
    return Dataset(data)


if __name__ == '__main__':
    # https://www.datacamp.com/community/tutorials/svm-classification-scikit-learn-python
    # pip install sklearn
    from sklearn import datasets
    #datset = datasets.load_breast_cancer()
    datset = loadData("tagging/car.csv")
    
    '''
    print("Features:", datset.feature_names)
    print("Labels:", datset.target_names)
    print("Shape:", datset.data.shape)
    print()
    print(datset.data[0:5])
    print(datset.target)
    '''
    
    from sklearn.model_selection import train_test_split
    # test_size indicates the percent of that data that should be used for testing. The rest is for training.
    X_train, X_test, y_train, y_test = train_test_split(datset.data, datset.target, test_size=0.3)
    
    from sklearn import svm
    clf = svm.SVC(kernel='linear')
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    from sklearn import metrics
    print()
    avgArg = "micro" # could be one of "macro", "micro", or "weighted"
    print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
    print("Precision:", metrics.precision_score(y_test, y_pred, average=avgArg))
    print("Recall:", metrics.recall_score(y_test, y_pred, average=avgArg))
    
    '''
    # Test on data like so
    test = clf.predict([[1.799e+01, 1.038e+01, 1.228e+02, 1.001e+03, 1.184e-01, 2.776e-01, 3.001e-01,
                         1.471e-01, 2.419e-01, 7.871e-02, 1.095e+00, 9.053e-01, 8.589e+00, 1.534e+02,
                         6.399e-03, 4.904e-02, 5.373e-02, 1.587e-02, 3.003e-02, 6.193e-03, 2.538e+01,
                         1.733e+01, 1.846e+02, 2.019e+03, 1.622e-01, 6.656e-01, 7.119e-01, 2.654e-01,
                         4.601e-01, 1.189e-01]])
    # It must be a 2D array, so you can test on multiple points at once
    print(test)
    '''
    