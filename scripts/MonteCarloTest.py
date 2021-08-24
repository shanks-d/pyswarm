from yaml.events import MappingStartEvent
import test_swarm
import pickle


RUNS = 10000
performance = []
failedData = []

for i in range(RUNS):
    success, posi = test_swarm.main()
    performance.append(success)
    if not success:
        print("current failures = ", len(performance) - sum(performance))
        failedData.append(posi)
    print("Progress = ", i/RUNS * 100, end = "\r")

print("Performance = ", sum(performance)/len(performance))
print("Failures = ", len(performance) - sum(performance))

with open("failedCases.pkl", "wb") as file:
    pickle.dump(failedData, file)