from libraries import *

line = "=================================="

print(line)
print("\t\tStock Predictor AI")
print(line)

dataSet = input("Create Data? (y/n): ")
createData = True

if dataSet == "y":
    createData = True
else:
    createData = False

input("Press Enter to create training data >> ")

batchTrainingData(showProgress=True, createData=True)