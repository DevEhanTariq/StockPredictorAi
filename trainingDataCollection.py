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

    def compileTickers(self): # Creates a list of all Stocks in nasdaqtrader
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        nasdaq = pd.read_csv(url, sep="|") # Webscrapes the url

        tickers = nasdaq["Symbol"].dropna().tolist()

        nyse_url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
        nyse = pd.read_csv(nyse_url, sep="|") # Webscrapes the url

        self.tickers = list(set(tickers + nyse["ACT Symbol"].dropna().tolist())) # Puts the list of Stocks in self.tickers variable

    def checkValidTickers(self, showStocks: bool=False): # Checks if all tickers are in Yahoo Finance
        ts = trainingSettings()
        searchLength = ts[1]
        for t in self.tickers[:searchLength]:  # Loops through all tickers and checks if they are in Yahoo Finance
            if  showStocks:
                print(t)
            try:
                if not yf.Tickers(t).history(period="5d", progress=False).empty:
                    self.validTickers.append(t)
            except:
                pass

if __name__ == "__main__":
    tdc = trainingDataCollection()
    tdc.compileTickers()
    tdc.checkValidTickers(showStocks=True)
    print(tdc.validTickers)