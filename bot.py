if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()  # Only run this part in dev env

import os
import logging
from telegram import ChatAction, ParseMode
from telegram.ext import CommandHandler, Updater

from data import loadTrainTimingData
from utils import cleanForMarkdown, getSimilarStations


TELEGRAM_TOKEN = os.environ["TELEGRAM_API"]  # Load in Telegram bot token
TRAIN_TIME_DATA = loadTrainTimingData(
    "train-timing.json"
)  # Load data from the json file

log = logging.getLogger()
log.debug("Starting bot...")


def command_queryStation(update, context):
    log.debug("Query from user %s", update.message.chat.username)
    log.debug("Message content: [%s]", update.message.text)

    queryParams = context.args
    if len(queryParams) == 0:
        update.message.reply_text("Please give me a station name!")
        log.debug("Ending since query is empty")
        return
    stationName = " ".join(queryParams)

    # Handle the case where user input doesn't exactly match
    if stationName not in TRAIN_TIME_DATA:
        log.debug('"%s" is not in list of station names', stationName)
        similarity = getSimilarStations(stationName, TRAIN_TIME_DATA.values())

        stationName = cleanForMarkdown(stationName)
        topSimRatio = similarity[0]["ratio"]
        topSimStation = similarity[0]["station"]

        log.debug(
            "Top similarity is %s, station is %s", str(topSimRatio), topSimStation.name
        )

        if 0.7 <= topSimRatio < 0.9:

            # Not that good, but good enough as the top suggestion
            update.message.reply_text(
                f"*Couldn't find {stationName}\!* Did you mean *_{topSimStation.getCleanedName()}_*?",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            update.message.reply_text(f"Here's a few more suggestions:")
            update.message.reply_text(
                "\n".join(
                    [
                        x["station"].getEmojiedName()
                        + " _\("
                        + str(round(100 * x["ratio"], 2))
                        + "% similar\)_"
                        for x in similarity[:5]
                    ]
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return
        elif topSimRatio < 0.7:
            # Suggest the top few names
            update.message.reply_text(
                f"*Couldn't find {stationName}\!* Here's some suggestions:",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            update.message.reply_text(
                "\n".join(
                    [
                        x["station"].getEmojiedName()
                        + " _\("
                        + cleanForMarkdown(str(round(100 * x["ratio"], 2)))
                        + "% similar\)_"
                        for x in similarity[:5]
                    ]
                ),  # replace . with \. for Markdown
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return

        # Only reach here if topSim['ratio'] is 0.9 or higher
        # Good enough match, use this as stationName instead
        stationName = topSimStation.getCleanedName()

    log.debug("Sending out info for %s", stationName)

    lineInformation = TRAIN_TIME_DATA[stationName].getLineInformation()
    timingsMessages = TRAIN_TIME_DATA[stationName].getFormattedTimings()

    # Send the station name + line information, followed by timing info in a new message
    update.message.reply_text(
        f"*{stationName} Station*\n_{lineInformation}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    for eachMsg in timingsMessages:
        update.message.reply_text(eachMsg, parse_mode=ParseMode.MARKDOWN_V2)

    log.debug("Query from %s completed", update.message.chat.username)


def command_start(update, context):
    log.debug("Start request from %s", update.message.chat.username)
    startMsg = "*Hello\! I'm LastTrainBot\.* Just use `/check <station name>` and I'll tell you the last times for that station\."
    update.message.reply_text(startMsg, parse_mode=ParseMode.MARKDOWN_V2)
    log.debug("Start request from %s completed", update.message.chat.username)


updater = Updater(TELEGRAM_TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", command_start))  # Start command

dispatcher.add_handler(
    CommandHandler("check", command_queryStation)
)  # Actual query command

log.debug("Bot started")
updater.start_polling()
