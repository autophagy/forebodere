============
Installation
============

Python
======

Forebodere exists as a package_ on PyPI and can be installed via pip::

    pip install forebodere

Docker
======

Forebodere also exists as a Docker_ image, and can be pulled::

    docker pull autophagy/forebodere:latest

However, if you wish to run Forebodere on a Raspberry Pi, you need to build
the Docker image on the Pi's own ARM processor::

    git clone git@github.com:autophagy/forebodere.git
    docker build -t autophagy/forebodere:latest forebodere


.. _package: https://pypi.org/project/forebodere/
.. _Docker: https://hub.docker.com/r/autophagy/forebodere/
