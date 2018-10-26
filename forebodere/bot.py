import discord
import asyncio
import time
import signal
import platform
import re

from datetime import datetime
from math import floor
from random import randint, choice

from whoosh.qparser import QueryParser
from whoosh import highlight

import markovify

from .models import QuoteEntry
from forebodere import version
from .register import FunctionRegister
from .buffer import MessageBuffer


class Bot(object):

    restart_time = 1
    restart_limit = 300
    queries = 0

    registry = FunctionRegister()

    def __init__(self, token, index, model, hord, logger):
        global LOGGER
        LOGGER = logger

        self.init = datetime.now()

        self.client = discord.Client()
        self.token = token
        self.index = index
        self.hord = hord
        self.model = model

        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        @self.client.event
        async def on_ready():
            self.restart_time = 1
            LOGGER.info(f"Connected as {self.client.user.name} ({self.client.user.id})")

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            command = message.content.split(" ", 1)[0]
            if self.registry.contains(command):
                LOGGER.info(
                    f"Recieved {command} from {message.author} ({message.guild} : {message.channel})"
                )
                self.queries += 1
                buf = self.registry.call(
                    command=command,
                    bot=self,
                    message=message.content[len(command) + 1 :].strip(),
                    author=message.author,
                )
                await message.channel.send(str(buf))

    @staticmethod
    def santise_quote(quote):
        """
        Within discord, custom emojis are formatted something similar to:
        <:customemoji:387878347>
        If a match on "custom" happens, the match formatter will insert ** into
        the emoji name, resulting in:
        <:**custom**emoji:387878347>
        Which breaks the formatting on the Discord client side.
        This removes any bolding asterisks from a quote within a custom emoji.
        """

        r = "<:[\w\d\*]*:[\d\*]*>"
        for match in re.findall(r, quote):
            quote = quote.replace(match, match.replace("*", ""))
        return quote

    def handle_signal(self, signum, frame):
        LOGGER.info(f"Recieved {signal.Signals(signum).name} signal")
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

            LOGGER.info(f"Waiting {self.restart_time} seconds to restart.")
            time.sleep(self.restart_time)
            self.restart_time = min(self.restart_time * 2, self.restart_limit)
        LOGGER.info("Exited.")

    @registry.register("!addquote")
    def add_quote(bot, message, author):
        """Adds a quote to the quote database."""
        buf = MessageBuffer()

        if message != "":
            try:
                with bot.index.writer() as writer:
                    largest_id = bot.index.doc_count() + 1
                    now = datetime.now()
                    bot.hord.insert(
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
                    markov_quote = message
                    forbidden_characters = "()\"'[]"
                    for character in forbidden_characters:
                        markov_quote = markov_quote.replace(character, "")
                    model = markovify.NewlineText(markov_quote)
                    if bot.model:
                        bot.model = markovify.combine([bot.model, model])
                    else:
                        bot.model = model
                buf.add("Added quote (id : {})".format(largest_id))
            except Exception as e:
                LOGGER.error("Failed to insert quote.")
                LOGGER.error(f"Quote: {format.message}")
                LOGGER.error(f"Submitter: {author}")
                LOGGER.error(f"Exception: {str(e)}")
                buf.add("Failed to add quote.")
        else:
            buf.add("No quote to add.")
        return buf

    @registry.register("!quote")
    def quote(bot, message, author):
        """
        Returns a quote. No argument returns a random quote.
        A text argument will search through the quote DB and return a random result.
        An argument of the form `id:69` will attempt to get the quote with the id of `69`.
        """
        buf = MessageBuffer()
        results = []

        if bot.index.doc_count() == 0:
            buf.add("No quotes have been added.")
            return buf

        with bot.index.searcher() as searcher:
            if message == "":
                i = randint(1, bot.index.doc_count())
                query = QueryParser("id", bot.index.schema).parse(str(i))
                results = searcher.search(query)
            else:
                query = QueryParser("quote", bot.index.schema).parse(message)
                results = searcher.search(query, limit=None)

            if len(results) > 0:
                results.formatter = BoldFormatter()
                results.fragmenter = highlight.WholeFragmenter()
                result = choice(results)
                quote = bot.santise_quote(result.highlights("quote", minscore=0))
                buf.add(f"[{result['id']}] {quote}")
                if "submitter" in result.keys() and "submitted" in result.keys():
                    buf.add(
                        f"*Submitted by {result['submitter']} on {result['submitted']}*."
                    )
            else:
                buf.add("No quote found.")

        return buf

    @registry.register("!markov")
    def markov(bot, message, author):
        """Generates a Markov chain from the quote corpus."""
        buf = MessageBuffer()
        try:
            sentence = bot.model.make_sentence(tries=1000)
            if sentence:
                buf.add(sentence)
            else:
                buf.add("Insufficient quote corpus to generate Markov chain.")
        except Exception as e:
            LOGGER.error("Failed to generate Markov chain.")
            LOGGER.error(e)
            buf.add("Failed to generate Markov chain.")
        return buf

    @registry.register("!status")
    def status(bot, message, author):
        """Returns information about the status of the Forebodere bot."""
        delta = datetime.now() - bot.init
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes = floor(remainder / 60)

        buf = MessageBuffer()
        buf.add("Bot Status:")
        buf.add_codeblock(
            f"""Quotes     ::   {bot.index.doc_count()}
                Queries    ::   {bot.queries}
                Uptime     ::   {floor(hours)}h{minutes}m
                Latency    ::   {round(bot.client.latency * 1000, 1)}ms
                Version    ::   {version}
            """
        )
        buf.add("System Status:")
        buf.add_codeblock(
            f"""Python     ::   {platform.python_version()}
                Platform   ::   {platform.platform()}
                Node       ::   {platform.node()}
            """
        )
        return buf

    @registry.register("!slap")
    def slap(bot, message, author):
        """🐟"""
        if message == "":
            target = author.name
        else:
            target = message
        buf = MessageBuffer()
        buf.add(
            f"*{bot.client.user.name} slaps {target} around a bit with a large trout*"
        )
        return buf


class BoldFormatter(highlight.Formatter):
    def format_token(self, text, token, replace=False):
        tokentext = highlight.get_text(text, token, replace)
        return f"**{tokentext}**"
