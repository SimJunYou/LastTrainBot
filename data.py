import json

TRAIN_LINE_NAME = {
    "NS": "North\-South Line",
    "EW": "East\-West Line",
    "CG": "East\-West Line _\(Airport Branch\)_",
    "NE": "North\-East Line",
    "CC": "Circle Line",
    "CE": "Circle Line _\(Marina Bay Branch\)_",
    "DT": "Downtown Line",
    "TE": "Thomson\-East Coast Line",
    "PT": "Punggol LRT Terminal",
    "PE": "Punggol LRT East Loop",
    "PW": "Punggol LRT West Loop",
    "ST": "Sengkang LRT Terminal",
    "SE": "Sengkang LRT East Loop",
    "SW": "Sengkang LRT West Loop",
    "BP": "Bukit Panjang LRT",
    "S": "Sentosa Monorail",
}

TRAIN_LINE_EMOJI = {
    "NS": "🔴",
    "EW": "🟢",
    "CG": "🟢",
    "NE": "🟣",
    "CC": "🟠",
    "CE": "🟠",
    "DT": "🔵",
    "TE": "🟤",
    "PT": "🚋", # Punggol LRT
    "PE": "🚋",
    "PW": "🚋",
    "ST": "🚋", # Sengkang LRT
    "SE": "🚋",
    "SW": "🚋",
    "BP": "🚋", # Bukit Panjang LRT
    "S": "🏖️",  # Sentosa
}


class TrainStation:
    def __init__(self, data):
        self.name = data["name"]
        self.codes = data["code"]
        allLinesTiming = [{x["line"]: x["timings"]} for x in data["lines"]]
        self.timings = allLinesTiming[0]
        if len(allLinesTiming) > 1:
            for eachLineTiming in allLinesTiming[1:]:
                self.timings.update(eachLineTiming)

    def getFormattedTimings(self):
        output = []
        for eachLine, eachTiming in self.timings.items():
            output.append(self.formatTiming(eachLine, eachTiming))
        return output

    def formatTiming(self, line, timing):
        template = f"*{TRAIN_LINE_EMOJI[line]} {TRAIN_LINE_NAME[line]}*\n\n"
        for eachDest in timing:
            subtemplate = f"Towards {eachDest['dest']}: *{eachDest['last']}*\n"
            template += subtemplate
        return template
    
    def getLineInformation(self):
        """ Returns multiple lines, each line is line color emojis + corresponding station code """
        output = []
        for eachCode in self.codes:
            if len(eachCode) == 2: # Sentosa train station
                output.append(TRAIN_LINE_EMOJI["S"] + " " + eachCode)
            else:
                output.append(TRAIN_LINE_EMOJI[eachCode[:2]] + " " + eachCode)
        return "\n".join(output)

    def getCleanedName(self):
        """ Escape all characters not compatible with MarkdownV2 """
        return self.name.replace("-", "\-")

    def getEmojiedName(self):
        """ Returns station name in bold with line color emojis at the back """
        emojis = []
        for eachCode in self.codes:
            if len(eachCode) == 2: # Sentosa train station
                emojis.append(TRAIN_LINE_EMOJI["S"])
            else:
                emojis.append(TRAIN_LINE_EMOJI[eachCode[:2]])
        return "*" + self.getCleanedName() + "* " + "".join(emojis)


def loadTrainTimingData(path):
    with open(path) as f:
        lastTrainData = json.load(f)
        allTrainStations = dict()
        stationNames = list()
        for eachStation in lastTrainData:
            allTrainStations[eachStation["name"]] = TrainStation(eachStation)
        return allTrainStations
