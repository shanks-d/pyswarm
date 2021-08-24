import pickle

with open("failedCases.pkl", "rb") as file:
    failedData = pickle.load(file)
for i in range(len(failedData)):
    print(failedData[i])