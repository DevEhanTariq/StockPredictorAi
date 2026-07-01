import yfinance as yf
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

if __name__ == "__main__":
    print(f"Torch version: {torch.__version__}")
    print(f"Numpy version: {np.__version__}")
    print(f"Pandas version: {pd.__version__}")
    print(f"YFinance version: {yf.__version__}")

