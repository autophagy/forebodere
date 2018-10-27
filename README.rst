.. image:: seonu/_static/github-header.png
    :alt: forebodere
    :align: center

Forebodere is a quotation bot for Discord, using the Whoosh_ search engine for
quote lookups.

Running
=======

Python
------

To run the bot directly with python, you should install the requirements in a
clean virtualenv and run the package, passing the path to hord and the discord bot
token (which can also be inferred from the ``$DISCORD_TOKEN`` environment variable)::

    virtualenv .venv -p python3.6
    source .venv/bin/activate

    pip install -r requirements.txt
    python -m forebodere --hord '/path/to/forebodere.hord' --token 'DISCORD_TOKEN'

Docker
------

A repository exists on Dockerhub_ for Forebodere, which can be pulled::

    docker pull autophagy/forebodere:latest

However, this will not run on ARM processors, like those on Raspberry Pi machines.
Instead, you should build the image directly on the machine::

    docker build -t autophagy/forebodere:latest .

You can then run the docker image by setting the ``DISCORD_TOKEN`` environment
variable ::

    docker run -d -e DISCORD_TOKEN="TOKEN" autophagy/forebodere:latest

However, due to the ephemeral nature of containers, the Quote DB will be deleted
upon container destruction. To create a persistant quote DB, pass in the
`forebodere.hord`_ as a volume::

    docker run -d -v /path/to/forebodere.hord:/app/forebodere.hord -e DISCORD_TOKEN="TOKEN" autophagy/forebodere:latest

.. image:: http://scieldas.autophagy.io/licenses/MIT.png
   :target: LICENSE
   :alt: MIT License

.. _Whoosh: https://whoosh.readthedocs.io/en/latest/intro.html
.. _Dockerhub: https://hub.docker.com/r/autophagy/forebodere/
.. _forebodere.hord: forebodere.hord
