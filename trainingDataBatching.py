from libraries import *

class trainingDataBatching: # Batches all training data into questions and answers for AI training
    def __init__(self):
        self.stockData: dict[str:dict] = None
        self.tickers: list[str] = []
        self.stockParameters: list[str] = []

        self.batches: list[list] = []

        self.period = trainingSettings()[0]
        self.interval = trainingSettings()[1]

    def loadStockData(self, showProgress: bool = False): # Loads training data
        with open("./TrainingData/stockData.json5", "r") as f: # Opens stockData.json5 as a read only file
            self.stockData = json5.load(f)
        for key in self.stockData.keys(): # Lists all Stocks in training data
            if showProgress:
                print(key)
            self.tickers.append(key)
        for key in self.stockData[self.tickers[0]].keys(): # Lists all parameters in training data
            self.stockParameters.append(key)

    def createBatches(self, showProgress: bool = False): # Creates batches
        if self.period == "1y" and self.interval == "1d":
            for ticker in self.tickers: # Loops through all tickers
                currentBatch = [[], []]
                for parameter in self.stockParameters: # Loops through all parameters
                    if parameter == "PercentIncrease":
                        currentBatch[1].append(self.stockData[ticker]["PercentIncrease"][-1]) # Saves the answer
                    currentParameterVals = self.stockData[ticker][parameter][:-1]
                    if showProgress:
                        print(ticker, parameter, len(currentParameterVals))
                    currentBatch[0].append(currentParameterVals) # Saves the question
                self.batches.append(currentBatch)
                if showProgress:
                    print(currentBatch)
        else:
            print("==============================")
            print("In trainingDataSettings.json5")
            print("period should be '1y'")
            print("interval should be '1d'")
            print("==============================")

        if showProgress:
            print(self.stockParameters)

def batchTrainingData(showProgress: bool = False, createTrainingData: bool = True):
    if showProgress:
        if createTrainingData:
            createTrainingData(showProgress=showProgress)
        print("Loading training data...")
        tdb = trainingDataBatching()
        tdb.loadStockData(showProgress=showProgress)
        print("Creating batches...")
        tdb.createBatches(showProgress=showProgress)
    else:
        if createTrainingData:
            createTrainingData(showProgress=showProgress)
        tdb = trainingDataBatching()
        tdb.loadStockData(showProgress=showProgress)
        tdb.createBatches(showProgress=showProgress)

if __name__ == "__main__":
    batchTrainingData(showProgress=True, createTrainingData=True)
