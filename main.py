import json


class TrainStation:
    def __init__(self, data):
        self.name = data["name"]
        allLinesTiming = [{x["line"]: x["timings"]} for x in data["lines"]]
        self.timings = allLinesTiming[0]
        if len(allLinesTiming) > 1:
            for eachLineTiming in allLinesTiming[1:]:
                self.timings.update(eachLineTiming)

    def getLastTiming(self):
        print(json.dumps(self.timings, indent=2))


with open("train-timing.json") as f:
    lastTrainData = json.load(f)
    allTrainStations = dict()
    for eachStation in lastTrainData:
        allTrainStations[eachStation["name"]] = TrainStation(eachStation)

    allTrainStations["Jurong East"].getLastTiming()
