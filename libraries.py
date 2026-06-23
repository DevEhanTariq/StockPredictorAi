import torch # Imports PyTorch
import torch.nn as nn # Imports all functions related to neural networks
import torch.optim as optim # Defines Optimiser
from torch.utils.data import Dataset, DataLoader # Handles training data

import yfinance as yf # Provides accsess to stock information

from os import write
import sys # why not
import json5 # To handle settings and store training data
import numpy as np # For manipulating data
import pandas as pd # For manipulating data
import matplotlib.pyplot as plt # For data visualisation
import math # For Sigmoid functions

from trainingDataCollection import createTrainingData, trainingSettings # For creating data and reading settings
from trainingDataBatching import batchTrainingData
from batchesToXYTensors import splitBatchesToXYTensors

if __name__ == "__main__":
    print(f"sys version: {sys.version}")
    print(f"Torch version: {torch.__version__}")
    print(f"Numpy version: {np.__version__}")
    print(f"Pandas version: {pd.__version__}")
    print(f"YFinance version: {yf.__version__}")
    print(f"JSON5 version: {json5.__version__}")

