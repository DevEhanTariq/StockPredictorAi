from pandas.core.arrays import period
from pygments.lexers import json5

from libraries import *

def trainingSettings():
    with open("./Settings/trainingDataSettings.json5", "r") as f:
        data = json5.load(f)
        permanentStock, period, interval, stockSearchAmount, start, end = data["permanentStock"], data["period"], data["interval"], data["stockSearchAmount"], data["start"], data["end"]
        return (period, interval, stockSearchAmount, start, end, permanentStock)

class trainingDataCollection:
    def __init__(self):
        self.tickers: list[str] = []
        self.validTickers: list[str] = []
        self.data: dict[str:] = {}

    def compileTickers(self): # Creates a list of all Stocks in nasdaqtrader
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        nasdaq = pd.read_csv(url, sep="|") # Webscrapes the url

        tickers = nasdaq["Symbol"].dropna().tolist()

        nyse_url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
        nyse = pd.read_csv(nyse_url, sep="|") # Webscrapes the url

        self.tickers = list(set(tickers + nyse["ACT Symbol"].dropna().tolist())) # Puts the list of Stocks in self.tickers variable

    def checkValidTickers(self, showStocks: bool=False, progressCheck: bool=False): # Checks if all tickers are in Yahoo Finance
        ts = trainingSettings()
        searchLength = ts[2]
        ts = trainingSettings()
        self.validTickers += ts[-1]
        for t in self.tickers[:searchLength]:  # Loops through all tickers and checks if they are in Yahoo Finance
            if  showStocks:
                print(t)
            try:
                if not yf.Tickers(t).history(period="5d", progress=progressCheck).empty:
                    self.validTickers.append(t)
            except:
                pass
        if showStocks:
            print(self.validTickers)

    def compileTrainingData(self, showStocks: bool=False): # Saves all data in a dictionary
        order = ["Open", "Close", "High", "Low", "Volume", "Dividends", "Stock Splits"] # The order the stock values are saved
        ts = trainingSettings()
        period = ts[0]
        interval = ts[1]
        stockSearchAmount = ts[2]
        start = ts[3]
        end = ts[4]
        for validTicker in self.validTickers: # Loops through all valid tickers
            if showStocks:
                print(validTicker) # Shows what Stock the loops on
            ticker = yf.Ticker(validTicker)
            if start == None and end == None:
                data = ticker.history(period=period, interval=interval)
            else:
                data = ticker.history(interval=interval, start=start, end=end)
            self.data[validTicker] = {}
            open = []
            close = []
            for od in order: # Loops through the order of the Stocks
                for column in data.columns: # Goes through every column
                    if column == od: # Checks if its in the correct order
                        self.data[validTicker][column] = data[column].tolist() # Adds it to the dict
                        if od == "Open":
                            open.append(data[column].tolist())
                        elif od == "Close":
                            close.append(data[column].tolist())
            percenteIncrease = []
            for i in range(len(open)):
                for j in range(len(open[i])):
                    percent = float(close[i][j]) / float(open[i][j])
                    percenteIncrease.append(percent)
            self.data[validTicker]["PercentIncrease"] = percenteIncrease

    def saveTrainingData(self): # Saves self.data to json5
        data = self.data
        with open("./TrainingData/stockData.json5", "w") as f: # Opens stockData.json5
            json5.dump(data, f, indent=4)

def createTrainingData(showProgress: bool=False):
    tdc = trainingDataCollection()  # Redefines the class as tdc
    if showProgress:
        print("Creating list of tickers...")
        tdc.compileTickers()
        print("Checking if Stocks are valid...")
        tdc.checkValidTickers(showStocks=True)
        print("Compiling training data...")
        tdc.compileTrainingData(showStocks=True)
        print("Saving training data...")
        tdc.saveTrainingData()
        print("Training data saved!")
    else:
        tdc.compileTickers()
        tdc.checkValidTickers()
        tdc.compileTrainingData()
        tdc.saveTrainingData()


if __name__ == "__main__":
    createTrainingData(showProgress=True)