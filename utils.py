from re import escape
from difflib import SequenceMatcher as SM


def cleanForMarkdown(msg):
    return escape(msg)


def getSimilarStations(stationName, allStations):
    similarity = [
        {
            "station": eachStation,
            "ratio": SM(None, eachStation.name, stationName).ratio(),
        }
        for eachStation in allStations
    ]
    similarity.sort(key=lambda x: x["ratio"], reverse=True)
    return similarity
