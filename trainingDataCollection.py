from pandas.core.arrays import period
from pygments.lexers import json5
from sympy.integrals.laplace import InverseLaplaceTransform

from libraries import *

def trainingSettings(): # Accesses trainingDataSettings.md
    with open("./Settings/trainingDataSettings.json5", "r") as f: # Opens the file as read only
        data = json5.load(f)
        permanentStock, period, interval, stockSearchAmount, start, end = data["permanentStock"], data["period"], data["interval"], data["stockSearchAmount"], data["start"], data["end"]
        return (period, interval, stockSearchAmount, start, end, permanentStock) # Returns all settings

def EMACalc(closingPrices: list, dayLength: int): # Calculates the EMA, given some parameters
    EMA = []
    alpha = 2/(dayLength + 1) # Finds the alpha
    Ialpha = 1-alpha # Finds what 1 - alpha is
    for i in range(len(closingPrices)): # Loops through all closing prices
        if i == 0: # If it is the loops first iteration, it appends the same value
            EMA.append(closingPrices[i])
        else: # Else is calculates EMA
            currentEMA = (closingPrices[i]*alpha) + (EMA[-1]*Ialpha)
            EMA.append(currentEMA)
    return EMA # Returns the EMA

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
                            open = (data[column].tolist())
                        elif od == "Close":
                            close = (data[column].tolist())

            percenteIncrease = []
            for j in range(len(open)):
                percent = float(close[j]) / float(open[j]) # Calculates percentage increase
                percenteIncrease.append(percent)
            self.data[validTicker]["PercentIncrease"] = percenteIncrease

            EMA_5 = EMACalc(close, 5)
            EMA_9 = EMACalc(close, 9)
            EMA_10 = EMACalc(close, 10)
            EMA_20 = EMACalc(close, 20)
            EMA_50 = EMACalc(close, 50)
            EMA_200 = EMACalc(close, 200)

            self.data[validTicker]["EMA_5"] = EMA_5
            self.data[validTicker]["EMA_9"] = EMA_9
            self.data[validTicker]["EMA_10"] = EMA_10
            self.data[validTicker]["EMA_20"] = EMA_20
            self.data[validTicker]["EMA_50"] = EMA_50
            self.data[validTicker]["EMA_200"] = EMA_200

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