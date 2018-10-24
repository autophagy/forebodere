# -*- coding: utf-8 -*-

from setuptools import setup
from forebodere import version

try:
    with open("README.rst", "r", encoding="utf-8") as f:
        readme = f.read()
except IOError:
    readme = ""


setup(
    name="forebodere",
    version=version,
    author="Mika Naylor (Autophagy)",
    author_email="mail@autophagy.io",
    description="Discord quote bot",
    long_description=readme,
    entry_points={"console_scripts": ["forebodere = forebodere.__main__:main"]},
    packages=["forebodere"],
    dependency_links=[
        "git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py-1.0.0a1590+g860d6a9"
    ],
    install_requires=[
        "Whoosh==2.7.4",
        "wisdomhord==0.3.1",
        "discord.py==1.0.0a1590+g860d6a9",
        "markovify==0.7.1",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
