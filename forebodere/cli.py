# -*- coding: utf-8 -*-

import argparse
import logging
import os

from whoosh.fields import Schema, ID, TEXT, STORED
from whoosh.index import create_in

import wisdomhord

from .models import QuoteEntry
from .bot import Bot

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
            required=True,
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
        self.hord = wisdomhord.hladan(args.hord, bisen=QuoteEntry)
        self.index = self.build_whoosh_index(args.index, self.hord)

        bot = Bot(args.token, self.index, self.hord, LOGGER)
        bot.run()

    def build_whoosh_index(self, index, hord):
        if not os.path.exists(index):
            os.mkdir(index)
        index = create_in(
            index,
            Schema(
                quote=TEXT(stored=True),
                ID=ID(stored=True),
                submitter=STORED,
                submitted=STORED,
            ),
        )
        with index.writer() as writer:
            LOGGER.info("Building Whoosh index from hord.")
            for row in hord.get_rows():
                if row.submitted:
                    submitted = row.submitted.strftime("%b %d %Y %H:%M:%S")
                else:
                    submitted = None
                writer.update_document(
                    quote=row.quote,
                    ID=str(row.id),
                    submitter=(row.submitter),
                    submitted=(submitted),
                )
        LOGGER.info("Index built. {} documents indexed.".format(index.doc_count()))
        return index

    def configure_logger(self, verbose: int):
        LOGGER.setLevel([logging.WARN, logging.INFO, logging.DEBUG][min(verbose, 2)])
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(LOGGER.level)
        LOGGER.addHandler(handler)


def main():
    try:
        Forebodere()
    except KeyboardInterrupt:
        print("\nExiting...\n")
        exit(0)
