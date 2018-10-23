import sys

from .buffer import MessageBuffer


class FunctionRegister(object):
    def __init__(self, help_command="!help"):
        self.commands = {}
        self.help_command = help_command
        self.commands[help_command] = self.help

    def register(self, command):
        def decorator(func):
            self.commands[command] = func

        return decorator

    def contains(self, command):
        return command in self.commands.keys()

    def call(self, command, **kwargs):
        func = self.commands.get(command)
        if command == self.help_command:
            return func()
        return func(**kwargs)

    def help(self):
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
        for command in sorted(self.commands.keys()):
            buf.add(f"• `{command}` - {trim(self.commands[command].__doc__)}")
        return buf
