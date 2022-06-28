from re import escape


def cleanForMarkdown(msg):
    return escape(msg)
