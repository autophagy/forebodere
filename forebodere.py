import argparse
import discord
import wisdomhord
from random import randint, choice

import logging

import os

from whoosh.fields import Schema, ID, TEXT
from whoosh.index import create_in
from whoosh.query import Term
from whoosh.qparser import QueryParser
from whoosh import highlight
from datetime import datetime
from math import floor

COMMANDS = {
    "`!quote`": "Returns a random quote.",
    "`!quote text`": "Returns a random quote that contains `text`.",
    "`!quote ID:69`": "Returns the quote with the ID of `69`.",
    "`!addquote text`": "Adds a quote with the content `text`.",
    "`!stats`": "Returns some stats.",
    "`!help`": "Prints this help.",
}


class QuoteEntry(wisdomhord.Bisen):
    __invoker__ = "Forebodere"
    __description__ = "Quotes"
    id = wisdomhord.Sweor("ID", wisdomhord.Integer)
    quote = wisdomhord.Sweor("QUOTE", wisdomhord.String)


class BoldFormatter(highlight.Formatter):
    def format_token(self, text, token, replace=False):
        tokentext = highlight.get_text(text, token, replace)
        return "**%s**" % tokentext


LOGGER = logging.getLogger("forebodere")

client = discord.Client()
hord = None

schema = Schema(quote=TEXT(stored=True), ID=ID(stored=True))

if not os.path.exists("index"):
    os.mkdir("index")

index = create_in("index", schema)

init = datetime.now()


def configure_logger(verbose: int):
    LOGGER.setLevel([logging.WARN, logging.INFO, logging.DEBUG][min(verbose, 2)])
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(LOGGER.level)
    LOGGER.addHandler(handler)


parser = argparse.ArgumentParser(description="Forebodere :: A Discord Quote Bot")
parser.add_argument("--hord")
parser.add_argument("--token")
parser.add_argument("-v", "--verbose", action="count", default=0)
args = parser.parse_args()
configure_logger(args.verbose)
hord = wisdomhord.hladan(args.hord, bisen=QuoteEntry)
with index.writer() as writer:
    LOGGER.info("Building index from hord.")
    for row in hord.get_rows():
        writer.update_document(quote=row.quote, ID=str(row.id))
LOGGER.info("Index built. {} documents indexed.".format(index.doc_count()))


def add_quote(quote):
    with index.writer() as writer:
        largest_id = index.doc_count() + 1
        hord.insert(QuoteEntry(id=largest_id, quote=quote))
        writer.update_document(quote=quote, ID=str(largest_id))
    return largest_id


def format_time_delta(time_delta):
    hours, remainder = divmod(time_delta.total_seconds(), 3600)
    minutes = floor(remainder / 60)
    return "{0}h{1}m".format(floor(hours), minutes)


@client.event
async def on_ready():
    LOGGER.info("Connected as {0} ({1})".format(client.user.name, client.user.id))


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.strip() == ("!quote"):
        LOGGER.info(
            "Recieved message '{0}' from {1}".format(message.content, message.author)
        )
        i = randint(0, index.doc_count())
        query = QueryParser("ID", index.schema).parse(str(i))
        with index.searcher() as searcher:
            result = searcher.search(query)[0]
            msg = "[{0}] {1}".format(result["ID"], result["quote"])
            await client.send_message(message.channel, msg)

    elif message.content.startswith("!quote "):
        LOGGER.info(
            "Recieved message '{0}' from {1}".format(message.content, message.author)
        )
        query = QueryParser("quote", index.schema).parse(message.content[7:])
        with index.searcher() as searcher:
            results = searcher.search(query, limit=None)
            LOGGER.info("Query: {0} // Results: {1}".format(query, len(results)))
            results.formatter = BoldFormatter()
            results.fragmenter = highlight.WholeFragmenter()
            if len(results) > 0:
                result = choice(results)
                msg = "[{0}] {1}".format(
                    result["ID"], result.highlights("quote", minscore=0)
                )
                await client.send_message(message.channel, msg)
            else:
                await client.send_message(
                    message.channel,
                    "No quote found for `{}`".format(message.content[7:]),
                )
    elif message.content.strip().startswith("!addquote "):
        new_id = add_quote(message.content.strip()[10:])
        await client.send_message(
            message.channel, "Added quote (ID: {})".format(new_id)
        )
    elif message.content.strip() == ("!stats"):
        await client.send_message(
            message.channel,
            "Forebodere is currently sheparding {} quotes.".format(index.doc_count()),
        )
        await client.send_message(
            message.channel,
            "Forebodere has been running for {}.".format(
                format_time_delta(datetime.now() - init)
            ),
        )
    elif message.content.strip() == ("!slap"):
        await client.send_message(
            message.channel,
            "*{0} slaps {1} around a bit with a large trout*".format(
                client.user.name, message.author
            ),
        )
    elif message.content.strip() == ("!help"):
        messages = []
        messages.append("Forebodere currently supports:")
        for command, desc in COMMANDS.items():
            messages.append("- {0} :: {1}".format(command, desc))
        await client.send_message(message.channel, "\n".join(messages))


LOGGER.info("Starting Discord client with token: {}".format(args.token))
client.run(args.token)
