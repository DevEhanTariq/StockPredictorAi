from libraries import *

class trainingDataBatching: # Batches all training data into questions and answers for AI training
    def __init__(self):
        self.stockData: dict[str:dict] = None
        self.tickers: list[str] = []
        self.stockParameters: list[str] = []

    def loadStockData(self): # Loads training data
        with open("./TrainingData/stockData.json5", "r") as f: # Opens stockData.json5 as a read only file
            self.stockData = json5.load(f)
        for key in self.stockData.keys(): # Lists all Stocks in training data
            self.tickers.append(key)
        for key in self.stockData[self.tickers[0]].keys(): # Lists all parameters in training data
            self.stockParameters.append(key)

    def createBatch(self):
        pass

def batchTrainingData(showProgress: bool = False):
    if showProgress:
        createTrainingData(showProgress=showProgress)
        print("Loading training data...")
        tdb = trainingDataBatching()
        tdb.loadStockData()
    else:
        createTrainingData(showProgress=showProgress)
        tdb = trainingDataBatching()
        tdb.loadStockData()

if __name__ == "__main__":
    batchTrainingData(showProgress=True)
