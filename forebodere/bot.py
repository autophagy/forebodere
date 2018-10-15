import discord

from datetime import datetime
from math import floor
from random import randint, choice
import sys

from whoosh.qparser import QueryParser
from whoosh import highlight

from .models import QuoteEntry
from forebodere import author as autophagy, license, source, version


class Bot(object):
    def __init__(self, token, index, hord, logger):
        global LOGGER
        LOGGER = logger

        self.init = datetime.now()

        self.client = discord.Client()
        self.token = token
        self.index = index
        self.hord = hord

        self.commands = {
            "!quote": self.quote,
            "!addquote": self.add_quote,
            "!status": self.status,
            "!slap": self.slap,
            "!help": self.help,
        }

        @self.client.event
        async def on_ready():
            LOGGER.info(
                "Connected as {0} ({1})".format(
                    self.client.user.name, self.client.user.id
                )
            )

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            command = message.content.split(" ", 1)[0]
            if command in self.commands:
                LOGGER.info(
                    "Recieved {} command from {} ({} : {})".format(
                        command, message.author, message.server, message.channel
                    )
                )
                func = self.commands.get(command)
                buf = func(message.content[len(command) + 1 :].strip(), message.author)
                await self.client.send_message(message.channel, str(buf))

    def add_quote(self, message, author):
        """Adds a quote to the quote database."""
        buf = MessageBuffer()

        if message != "":
            try:
                with self.index.writer() as writer:
                    largest_id = self.index.doc_count() + 1
                    self.hord.insert(QuoteEntry(id=largest_id, quote=message))
                    writer.update_document(quote=message, ID=str(largest_id))
                buf.add("Added quote (ID : {})".format(largest_id))
            except Exception as e:
                LOGGER.error("Failed to insert quote.")
                LOGGER.error("Quote: {}".format(message))
                LOGGER.error("Submitter: {}".format(author))
                LOGGER.error("Exception: {}".format(str(e)))
                buf.add("Failed to add quote.")
        else:
            buf.add("No quote to add.")
        return buf

    def quote(self, message, author):
        """
        Returns a quote. No argument returns a random quote.
        A text argument will search through the quote DB and return a random result.
        An argument of the form `ID:69` will attempt to get the quote with the ID of `69`.
        """
        buf = MessageBuffer()
        results = []

        with self.index.searcher() as searcher:
            if message == "":
                i = randint(0, self.index.doc_count())
                query = QueryParser("ID", self.index.schema).parse(str(i))
                results = searcher.search(query)
            else:
                query = QueryParser("quote", self.index.schema).parse(message)
                results = searcher.search(query, limit=None)

            if len(results) > 0:
                results.formatter = BoldFormatter()
                results.fragmenter = highlight.WholeFragmenter()
                result = choice(results)
                buf.add(
                    "[{0}] {1}".format(
                        result["ID"], result.highlights("quote", minscore=0)
                    )
                )
            else:
                buf.add("No quote found.")

        return buf

    def status(self, message, author):
        """Returns information about the status of the Forebodere bot."""
        delta = datetime.now() - self.init
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes = floor(remainder / 60)

        buf = MessageBuffer()
        buf.add("Forebodere is serving {} quotes.".format(self.index.doc_count()))
        buf.add(
            "Forebodere has been running for {0}h{1}m.".format(floor(hours), minutes)
        )
        buf.add(
            "Forebodere {} was cobbled together by {}. The source ({}) is available at {}".format(
                version, autophagy, license, source
            )
        )
        return buf

    def slap(self, message, author):
        """🐟"""
        if message == "":
            target = author.name
        else:
            target = message
        buf = MessageBuffer()
        buf.add(
            "*{0} slaps {1} around a bit with a large trout*".format(
                self.client.user.name, target
            )
        )
        return buf

    def help(self, message, author):
        """Returns information about valid Forebodere commands."""

        def trim(docstring):
            if not docstring:
                return ""
            # Convert tabs to spaces (following the normal Python rules)
            # and split into a list of lines:
            lines = docstring.expandtabs().splitlines()
            # Determine minimum indentation (first line doesn't count):
            indent = sys.maxsize
            for line in lines[1:]:
                stripped = line.lstrip()
                if stripped:
                    indent = min(indent, len(line) - len(stripped))
            # Remove indentation (first line is special):
            trimmed = [lines[0].strip()]
            if indent < sys.maxsize:
                for line in lines[1:]:
                    trimmed.append(line[indent:].rstrip())
            # Strip off trailing and leading blank lines:
            while trimmed and not trimmed[-1]:
                trimmed.pop()
            while trimmed and not trimmed[0]:
                trimmed.pop(0)
            # Return a single string:
            return "\n".join(trimmed)

        buf = MessageBuffer()
        buf.add("Forebodere supports:")
        for command in self.commands:
            buf.add(
                "• `{0}` - {1}".format(command, trim(self.commands[command].__doc__))
            )
        return buf

    def run(self):
        self.client.run(self.token)


class MessageBuffer(object):
    def __init__(self):
        self.messages = []

    def add(self, message):
        self.messages.append(message)

    def __str__(self):
        return "\n".join(self.messages)


class BoldFormatter(highlight.Formatter):
    def format_token(self, text, token, replace=False):
        tokentext = highlight.get_text(text, token, replace)
        return "**%s**" % tokentext
