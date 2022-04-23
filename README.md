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

This application was designed to work on Linux and has been tested in the following distros:

* Manjaro (Tested on 21.2.5)

<!-- More Soon -->

# Installation

The preffered method for running this bot is Docker.

Before running, don't forget to modify the `config.example.json5` file in the `./bot`
directory [(see below)](#configuration).

Installation commands:

```bash
git clone https://github.com/Clutter-Development/Clutter # Clone the repo
cd Clutter # Go to the Clutter directory
./deploy.sh # Run the deploy script
```

# Configuration

The bot configuration can be found in the `config.example.json5` file in the `./bot` directory.

There is already an example configuration in the file, so this chapter will not be very long.

If you want to use an .env file to store critical info (mongodb URI, bot token, error webhook), you can set
the `USE_ENV` key to `true` in the `config.example.json5` file. This will make it, so you need to put the critical info
in the env and not in the json file.
> Don't forget to rename `config.example.json5` to `config.json5`

Example env file:

```
DATABASE_URI=
BOT_TOKEN=
ERROR_WEBHOOK_URL=
LOG_WEBHOOK_URL=
```
