<div align="center">
    <p style="margin-bottom: 0 !important;">
        <img alt="Clutter Logo" src="https://github.com/Clutter-Development/clutter-development.github.io/blob/master/assets/logo.png" width=200>
    </p>
    <h1 style="font-size: 3em">Clutter</h1>

[![CodeFactor](https://www.codefactor.io/repository/github/clutter-development/clutter/badge)](https://www.codefactor.io/repository/github/clutter-development/clutter)
![Total Lines](https://img.shields.io/tokei/lines/github/Clutter-Development/Clutter)
[![License](https://img.shields.io/badge/license-GPL_3.0-success)](LICENSE)
[![Discord](https://img.shields.io/discord/944535258722861106?color=success&label=discord&logo=discord&logoColor=white)](https://discord.gg/mVKkMZRPQE)
</div>

Clutter is a multipurpose, compact, extremely configurable Discord bot.

# Installation

The preffered method for running this bot is Docker. <!-- currently broken -->

Before running, don't forget to modify the `config.example.json5` file in the `./bot`
directory [(see below)](#configuration).

Installation commands:

Docker installation:

```bash
git clone https://github.com/Clutter-Development/Clutter  # Clone the repository.
cd Clutter  # Go to the Clutter directory.
./deploy.sh  # Run the deploy script.
```

Traditional installation:

```bash
git clone https://github.com/Clutter-Development/Clutter  # Clone the repository.
cd Clutter  # Go to the Clutter directory.
python bot  # Run the bot.
```

# Configuration

The bot configuration can be found in the `config.example.json5` file in the `./bot` directory.

Don't forget to rename `config.example.json5` to `config.json5`.