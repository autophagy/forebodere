from discord import TextChannel, User
from collections import namedtuple
from datetime import datetime
import asyncio

ChannelTracker = namedtuple("ChannelTracker", "channel frequency last author")


class LolHandler(object):

    laughs = ["lol", "lmao", "rofl", "haha"]

    def __init__(self):
        self.tracker = {}

    def handle(self, message: str, channel: TextChannel, author: User):
        if channel.id not in self.tracker:
            self.tracker[channel.id] = ChannelTracker(
                channel=channel, frequency=0, last=datetime.now(), author=None
            )
        ct = self.tracker[channel.id]
        if message in self.laughs:
            if ct.author != author:
                self.tracker[channel.id] = ChannelTracker(
                    channel=ct.channel,
                    frequency=ct.frequency + 1,
                    last=datetime.now(),
                    author=author,
                )
        else:
            self.tracker[channel.id] = ChannelTracker(
                channel=ct.channel, frequency=0, last=datetime.now(), author=None
            )

    async def tick(self):
        while True:
            for id, tracker in self.tracker.items():
                if (
                    datetime.now() - tracker.last
                ).seconds >= 5 and tracker.frequency >= 3:
                    if tracker.frequency == 3:
                        await tracker.channel.send("Multilol!")
                    elif tracker.frequency == 4:
                        await tracker.channel.send("Ultralol!")
                    elif tracker.frequency > 4:
                        await tracker.channel.send("M-M-M-MONSTERLOL!")
                    self.tracker[id] = ChannelTracker(
                        channel=tracker.channel,
                        frequency=0,
                        last=datetime.now(),
                        author=None,
                    )
            await asyncio.sleep(2)
