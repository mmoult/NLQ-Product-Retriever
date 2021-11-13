def appendLineForLine(dataset, column):
    newDataset = []
    for i in range(len(column)):
        dEnd = dataset[i].find('/')
        newDataset.append(dataset[i][:dEnd] + ',' + column[i])
    return newDataset

def readInData(path):
    lines = []
    with open(path, 'r', encoding='utf-8') as reader:
        lines = reader.readlines()
    return lines

def writeNewDataset(lines, path):
    with open(path, 'w', encoding='utf-8') as writer:
            writer.writelines(lines)

def insertColumn(datasetPath, newDatasetPath, columnPath):
    dataset = readInData(datasetPath)
    column = readInData(columnPath)

    newDataset = appendLineForLine(dataset, column)

    writeNewDataset(newDataset, newDatasetPath)

if __name__ == '__main__':
    carsColPaths = ["cars/cylinders"]
    motorcyclesColPaths = ["motorcycles/owners"]
    csjobsColPaths = ["csjobs/revenue_min", "csjobs/revenue_max", "csjobs/salary_min", "csjobs/salary_max", "csjobs/size_min", "csjobs/size_max"]

    carsPath = "Datasets/vehicles4.csv"
    motorcyclesPath = "Datasets/BIKE-DETAILS.csv"
    csjobsPath = "Datasets/DataScientist.csv"

    carsPathNew = "int_Datasets/vehicles4.csv"
    motorcyclesPathNew = "int_Datasets/BIKE-DETAILS.csv"
    csjobsPathNew = "int_Datasets/DataScientist.csv"

    for colPath in carsColPaths:
        insertColumn(carsPath, carsPathNew, colPath)
    for colPath in motorcyclesColPaths:
        insertColumn(motorcyclesPath, motorcyclesPathNew, colPath)
    for colPath in csjobsColPaths:
        insertColumn(csjobsPath, csjobsPathNew, colPath)
