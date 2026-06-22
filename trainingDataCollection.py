from os import write

from pygments.lexers import json5

from libraries import *

def trainingSettings():
    with open("./Settings/trainingDataSettings.json5", "r") as f:
        data = json5.load(f)
        period = data["period"] # How long the data extends back in time
        stockSearchAmount = data["stockSearchAmount"] # How many stocks to search
        return (period, stockSearchAmount)

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
        searchLength = ts[1]
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

    def compileTrainingData(self, progressCheck: bool=False): # Saves all data in a dictionary
        ts = trainingSettings()
        periodTime: str = ts[0]

        validTickerString: str = ""
        for i in range(len(self.validTickers)): # Creates a string containing all valid tickers
            if self.validTickers[i] == self.validTickers[-1]:
                validTickerString += self.validTickers[i]
            else:
                validTickerString += self.validTickers[i] + " "
        tickers = yf.Tickers(validTickerString)

        hist = tickers.history(period=periodTime, progress=progressCheck)
        for j in range(len(self.validTickers)):  # Loops through all Stocks in Yahoo Finance
            histNew = hist[j]
            rows = hist.values.tolist()
            self.data[self.validTickers[j]] = rows

    def saveTrainingData(self): # Saves self.data to json5
        data = self.data
        with open("./TrainingData/stockData.json5", "w") as f: # Opens stockData.json5
            json5Data = json5.loads(data)
            json5.dump(json5Data, f)

if __name__ == "__main__":
    tdc = trainingDataCollection() # Redefines the class as tdc
    tdc.compileTickers()
    tdc.checkValidTickers(showStocks=True)
    #tdc.compileTrainingData()
    #tdc.saveTrainingData()