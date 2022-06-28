if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()  # Only run this part in dev env

import os
from telegram import Update, ChatAction, ParseMode
from telegram.ext import CommandHandler, Updater
from difflib import SequenceMatcher as SM

from data import loadTrainTimingData
from utils import cleanForMarkdown

TELEGRAM_TOKEN = os.environ["TELEGRAM_API"]  # Load in Telegram bot token
TRAIN_TIME_DATA = loadTrainTimingData(
    "train-timing.json"
)  # Load data from the json file


def send_typing_action(func):
    """Sends typing action while processing func command."""

    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return command_func


def temp_send_typing_action(update, context):
    context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
    )


@send_typing_action
def command_queryStation(update, context):
    queryParams = context.args
    if len(queryParams) == 0:
        update.message.reply_text("Please give me a station name!")
        return
    stationName = " ".join(queryParams)

    # Handle the case where user input doesn't exactly match
    if stationName not in TRAIN_TIME_DATA:
        similarity = [
            {
                "station": eachStation,
                "ratio": SM(None, eachStation.name, stationName).ratio(),
            }
            for eachStation in TRAIN_TIME_DATA.values()
        ]
        similarity.sort(key=lambda x: x["ratio"], reverse=True)

        stationName = cleanForMarkdown(stationName)
        topSimRatio = similarity[0]["ratio"]
        topSimStation = similarity[0]["station"]

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

    lineInformation = TRAIN_TIME_DATA[stationName].getLineInformation()
    timingsMessages = TRAIN_TIME_DATA[stationName].getFormattedTimings()

    update.message.reply_text(
        f"*{stationName} Station*\n_{lineInformation}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    for eachMsg in timingsMessages:
        temp_send_typing_action(update, context)
        update.message.reply_text(eachMsg, parse_mode=ParseMode.MARKDOWN_V2)


updater = Updater(TELEGRAM_TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(
    CommandHandler("start", command_queryStation)
)  # Making a handler for the type Update

updater.start_polling()
