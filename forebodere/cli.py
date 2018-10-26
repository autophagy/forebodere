# -*- coding: utf-8 -*-

import argparse
import logging
import os

from whoosh.fields import Schema, ID, TEXT, STORED
from whoosh.index import create_in

import wisdomhord

from .models import QuoteEntry
from .bot import Bot

import markovify

global LOGGER
LOGGER = logging.getLogger("forebodere")


class Forebodere(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Forebodere :: A Discord Quote Bot"
        )
        parser.add_argument(
            "--hord",
            type=str,
            metavar="HORD",
            required=True,
            help="Path to the quote hord to use.",
        )
        parser.add_argument(
            "--token",
            type=str,
            metavar="TOKEN",
            default=os.environ.get("DISCORD_TOKEN", None),
            help="Discord bot token.",
        )
        parser.add_argument(
            "--index",
            type=str,
            metavar="INDEX",
            help="Path to the Whoosh index.",
            default=".index",
        )
        parser.add_argument("-v", "--verbose", action="count", default=0)
        args = parser.parse_args()

        self.configure_logger(args.verbose)
        hord_path = os.path.expanduser(args.hord)
        if not os.path.exists(hord_path):
            hord = wisdomhord.cennan(hord_path, bisen=QuoteEntry)
        else:
            hord = wisdomhord.hladan(hord_path, bisen=QuoteEntry)
        index, model = self.build_indexes(args.index, hord)

        bot = Bot(args.token, index, model, hord, LOGGER)
        bot.run()

    @staticmethod
    def build_indexes(index, hord):
        if not os.path.exists(index):
            os.mkdir(index)
        index = create_in(
            index,
            Schema(
                quote=TEXT(stored=True),
                id=ID(stored=True),
                submitter=STORED,
                submitted=STORED,
            ),
        )
        corpus = []
        with index.writer() as writer:
            LOGGER.info("Building Whoosh index and markov model from hord.")
            for row in hord.get_rows():
                corpus.append(row.quote)
                if row.submitted:
                    submitted = row.submitted.strftime("%b %d %Y %H:%M:%S")
                else:
                    submitted = None
                writer.update_document(
                    quote=row.quote,
                    id=str(row.id),
                    submitter=(row.submitter),
                    submitted=(submitted),
                )
        LOGGER.info(f"Index built. {index.doc_count()} documents indexed.")
        if len(corpus) > 0:
            model = markovify.NewlineText("\n".join(corpus))
        else:
            model = None
        LOGGER.info(f"Markov model built.")
        return index, model

    def configure_logger(self, verbose: int):
        LOGGER.setLevel([logging.WARN, logging.INFO, logging.DEBUG][min(verbose, 2)])
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(LOGGER.level)
        LOGGER.addHandler(handler)


def main():
    Forebodere()
