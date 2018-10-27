=====
Usage
=====

Running The Bot
===============

Python
------

To run Forebodere, you will need to create a `Discord application`_, create a
bot_ and generate a token. With this token, you can then run Forebodere by either
passing in the path to the quote hord and token as arguments::

    forbodere --hord /path/to/forebodere.hord --token discord_token

or by exporting the token to the ``DISCORD_TOKEN`` environment variable::

    export DISCORD_TOKEN=discord_token
    forebodere --hord /path/to/forebodere.hord

Docker
------

To run Forebodere with Docker, you should pass in the discord token you generated
as an environment variable::

    docker run -e DISCORD_TOKEN=discord_token autophagy/forebodere:latest

However, this will create a quote hord within the container that will not survive
when the container is destroyed. To have a persistent quote hord, mount the
`empty hord`_ ::

    docker run -v /path/to/forebodere.hord:/app/forebodere.hord \
    -e DISCORD_TOKEN=discord_token autophagy/forebodere:latest

Commands
========

``!addquote``
-------------

Using the command ``!addquote`` will add any text after the command as a quote,
including the submitter and the datetime it was submitted.

``!help``
---------

This command returns all valid Forebodere commands, as well as a brief description.

``!markov``
-----------

This generates a `Markov chain`_ from the quote hord and returns it to the channel.
This command may not return anything if the quote hord is too small for a sufficiently
novel chain to be generated.

``!quote``
..........

Using this command by itself as ``!quote`` will return a random quote from the
quote hord. If the command is followed by text, such as ``!quote hello world``,
the bot will attempt to return a random quote that contains the text ``hello world``.
If the text that follows the command is of the form ``!quote id:10``, it will
attempt to return the quote with the id of 10.

``!slap``
.........

Please don't sue me, Khaled Mardam-Bey.

``!status``
...........

Returns the status of the bot (such as quotes, latency, uptime) and of the
underlying system (Python version, node name, platform).

.. _Discord application: https://discordapp.com/developers/applications/
.. _bot: https://discordapp.com/developers/docs/topics/oauth2#bots
.. _empty hord: https://github.com/autophagy/forebodere/blob/master/forebodere.hord
.. _Markov chain: https://en.wikipedia.org/wiki/Markov_chain
