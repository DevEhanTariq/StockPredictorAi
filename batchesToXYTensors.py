from libraries import *

def sigmoid(x):
    return 1 / (1 + math.exp(-x)) # Equation for a Sigmoid function

def Isigmoid(y):
    return math.log(y / (1 - y)) # Equation for an Inverse Sigmoid function

def minMaxNormalize(values):
    min_val = min(values)
    max_val = max(values)

    if min_val == max_val:
        return [0.0] * len(values)

    return [
        (x - min_val) / (max_val - min_val)
        for x in values
    ]

class batchesToXYTensors:
    def __init__(self):
        self.X = []
        self.Y = []

        self.batchData = []

    def loadBatchesData(self):
        with open("./TrainingData/stockBatchesData.json5", "r") as f:
            self.batchData = json5.load(f)

    def splitIntoXyTensors(self):
        for ticker in range(len(self.batchData)):
            exampleInput = []
            for parameter in range(len(self.batchData[ticker][0])):
                for value in minMaxNormalize(self.batchData[ticker][0][parameter]):
                    exampleInput.append(value)
            self.Y.append([sigmoid(self.batchData[ticker][1][0])])
            self.X.append(exampleInput)

def splitBatchesToXYTensors(showProgress: bool = False):
    btxyt = batchesToXYTensors()
    btxyt.loadBatchesData()
    btxyt.splitIntoXyTensors()
    if showProgress:
        print(btxyt.X[0])
        print(btxyt.Y[0])
        print(len(btxyt.X))
        print(len(btxyt.Y))
    return (btxyt.X, btxyt.Y)

if __name__ == '__main__':
    splitBatchesToXYTensors()