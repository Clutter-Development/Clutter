<div align="center">
    <p style="margin-bottom: 0 !important;">
        <img alt="Clutter Logo" src="https://github.com/Clutter-Development/clutter-development.github.io/blob/master/assets/logo.png" width=200>
    </p>
    <h1 style="font-size: 3em">Clutter</h1>

[![CodeFactor](https://www.codefactor.io/repository/github/clutter-development/clutter/badge)](https://www.codefactor.io/repository/github/clutter-development/clutter)
[![Total Lines](https://img.shields.io/tokei/lines/github/Clutter-Development/Clutter)](https://github.com/Clutter-Development/Clutter)
[![License](https://img.shields.io/badge/license-GPL_3.0-success)](./clutter/LICENSE)
[![Discord](https://img.shields.io/discord/944535258722861106?color=success&label=discord&logo=discord&logoColor=white)](https://discord.gg/mVKkMZRPQE)
</div>

#### Clutter is a multipurpose, compact and easy to use Discord bot. <!-- common sense is required btw -->

# Installation

The preffered method for running this bot is Docker. <!-- currently broken -->

Before running these commands, don't forget to modify the `config.example.json5` file in the `clutter`
directory [(see below)](#configuration).

## Installation Commands

### Docker Installation

> This installation requires [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) to be installed on your machine.

```bash
git clone https://github.com/Clutter-Development/Clutter  # Clone the repository.
cd Clutter  # Go to the Clutter directory.
./deploy.sh  # Run the deploy script.
```

### Traditional Installation

```bash
git clone https://github.com/Clutter-Development/Clutter  # Clone the repository.
cd Clutter  # Go to the Clutter directory.
pip install poetry && poetry install --no-dev  # Install dependencies.
python clutter  # Run the bot.
```

# Configuration

An example for the bot configuration can be found in the `config.example.json5` file in the `clutter` directory.

Don't forget to rename `config.example.json5` to `config.json5`.

# License

All code in this repository is licensed with the GNU General Public License v3, excluding the `clutter/utils` directory
which is licensed with the MIT license.
