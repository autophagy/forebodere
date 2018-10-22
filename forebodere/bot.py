import discord

from datetime import datetime
from math import floor
from random import randint, choice
import sys

from whoosh.qparser import QueryParser
from whoosh import highlight

from .models import QuoteEntry
from forebodere import version

import asyncio
import time

import signal

import platform


class Bot(object):

    restart_time = 1
    restart_limit = 300

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
            "!slap": self.slap,
            "!status": self.status,
            "!help": self.help,
        }

        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        @self.client.event
        async def on_ready():
            self.restart_time = 1
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
                        command, message.author, message.guild, message.channel
                    )
                )
                func = self.commands.get(command)
                buf = func(message.content[len(command) + 1 :].strip(), message.author)
                await message.channel.send(str(buf))

    def add_quote(self, message, author):
        """Adds a quote to the quote database."""
        buf = MessageBuffer()

        if message != "":
            try:
                with self.index.writer() as writer:
                    largest_id = self.index.doc_count() + 1
                    now = datetime.now()
                    self.hord.insert(
                        QuoteEntry(
                            id=largest_id,
                            quote=message,
                            submitter=str(author),
                            submitted=now,
                        )
                    )
                    writer.update_document(
                        quote=message,
                        id=str(largest_id),
                        submitter=str(author),
                        submitted=now.strftime("%b %d %Y %H:%M:%S"),
                    )
                buf.add("Added quote (id : {})".format(largest_id))
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
        An argument of the form `id:69` will attempt to get the quote with the id of `69`.
        """
        buf = MessageBuffer()
        results = []

        with self.index.searcher() as searcher:
            if message == "":
                i = randint(0, self.index.doc_count())
                query = QueryParser("id", self.index.schema).parse(str(i))
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
                        result["id"], result.highlights("quote", minscore=0)
                    )
                )
                if "submitter" in result.keys() and "submitted" in result.keys():
                    buf.add(
                        "*Submitted by {} on {}*".format(
                            result["submitter"], result["submitted"]
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
        buf.add("Bot Status:")
        buf.add("```")
        buf.add("Quotes     ::   {}".format(self.index.doc_count()))
        buf.add("Uptime     ::   {0}h{1}m".format(floor(hours), minutes))
        buf.add("Latency    ::   {}ms".format(round(self.client.latency * 1000, 1)))
        buf.add("Version    ::   {}".format(version))
        buf.add("```")
        buf.add("System Status:")
        buf.add("```")
        buf.add("Python     ::   {}".format(platform.python_version()))
        buf.add("Platform   ::   {}".format(platform.platform()))
        buf.add("Node       ::   {}".format(platform.node()))
        buf.add("```")
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

    def handle_signal(self, signum, frame):
        LOGGER.info("Recieved {} signal".format(signal.Signals(signum).name))
        raise SystemExit

    def exit(self):
        self.client.loop.run_until_complete(self.client.logout())
        for task in asyncio.Task.all_tasks(loop=self.client.loop):
            if task.done():
                task.exception()
                continue
            task.cancel()
            try:
                self.client.loop.run_until_complete(
                    asyncio.wait_for(task, 5, loop=self.client.loop)
                )
                task.exception()
            except asyncio.InvalidStateError:
                pass
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                pass
        self.client.loop.close()

    def run(self):
        loop = asyncio.get_event_loop()
        while True:
            try:
                LOGGER.info("Starting Discord bot.")
                loop.run_until_complete(self.client.start(self.token))
            except (KeyboardInterrupt, SystemExit):
                LOGGER.info("Exiting...")
                self.exit()
                break
            except Exception as e:
                LOGGER.error(e)

            LOGGER.info("Waiting {} seconds to restart.".format(self.restart_time))
            time.sleep(self.restart_time)
            self.restart_time = min(self.restart_time * 2, self.restart_limit)
        LOGGER.info("Exited.")


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
