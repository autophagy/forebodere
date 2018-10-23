class MessageBuffer(object):
    def __init__(self):
        self.messages = []

    def add(self, message):
        self.messages += list(map(lambda l: l.strip(), message.split("\n")))

    def add_codeblock(self, codeblock):
        self.add("```")
        self.add(codeblock)
        self.add("```")

    def __str__(self):
        return "\n".join(self.messages)
