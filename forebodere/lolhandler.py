from discord import TextChannel
from collections import namedtuple
from datetime import datetime
import asyncio

ChannelTracker = namedtuple("ChannelTracker", "channel frequency last")


class LolHandler(object):
    def __init__(self):
        self.tracker = {}

    def handle(self, message: str, channel: TextChannel):
        if channel.id not in self.tracker:
            self.tracker[channel.id] = ChannelTracker(
                channel=channel, frequency=0, last=datetime.now()
            )
        ct = self.tracker[channel.id]
        if message == "lol":
            self.tracker[channel.id] = ChannelTracker(
                channel=ct.channel, frequency=ct.frequency + 1, last=datetime.now()
            )

    async def tick(self):
        while True:
            for id, tracker in self.tracker.items():
                if (datetime.now() - tracker.last).seconds >= 5:
                    if tracker.frequency == 3:
                        await tracker.channel.send("Multilol!")
                    elif tracker.frequency == 4:
                        await tracker.channel.send("Ultralol!")
                    elif tracker.frequency > 4:
                        await tracker.channel.send("M-M-M-MONSTERLOL!")
                    self.tracker[id] = ChannelTracker(
                        channel=tracker.channel, frequency=0, last=datetime.now()
                    )
            await asyncio.sleep(2)
