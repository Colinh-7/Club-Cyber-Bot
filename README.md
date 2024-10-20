# Cyber Club Discord Bot

A Discord bot designed to interact with the [Root Me](https://api.www.root-me.org/) API, providing information about challenges, users, and statistics directly in a Discord server. This bot is used to facilitate cybersecurity learning and to manage weekly challenges within the Cyber Club.

## Features

- Fetch and display Root Me challenge information.
- Track weekly challenges and post updates in Discord.
- Display user statistics from Root Me (score, rank, challenges completed).
- Manage a leaderboard for club members participating in Root Me challenges.
- Announce the start and end of weekly challenges.

## Installation

### Requirements

- [Python 3.8+](https://www.python.org/)
- [discord.py](https://discordpy.readthedocs.io/en/stable/) library for interacting with the Discord API.
- Access to the [Root Me API](https://api.www.root-me.org/).

## Commands

### Challenge Commands

- `!weekly`: Add a weekly challenge, with a link to the Root Me page.

### User Commands

- `!stats [username]`: Fetches and displays Root Me user statistics including rank, score, and completed challenges.
- `!leaderboard`: Displays the current leaderboard of members based on Root Me statistics (WIP).

## Example of a Challenge Announcement

```plaintext
**Weekly Challenge added: Web - SQL Injection**

**Challenge Name**: Web - SQL Injection
**Category**: Web
**Difficulty**: Medium
**Score**: 50 points
[Click here to access the challenge](https://www.root-me.org/en/Challenges/Web/Web-SQL-Injection)
```

## Dependencies

- [`discord.py`](https://discordpy.readthedocs.io/en/stable/): To interact with Discord API.
- [`requests`](https://docs.python-requests.org/en/latest/): For making API requests to Root Me.

Install dependencies with:

```bash
pip install discord.py requests
```

## API Reference

### Root Me API

The bot interacts with the [Root Me](https://api.www.root-me.org/) platform by accessing its publicly available data on challenges and user statistics. Endpoints used by the bot include:

- `/challenges/[id]`: Retrieves information about a specific challenge.
- `/users/[username]`: Retrieves user statistics, including rank, score, and completed challenges.

### Discord API

The bot is built using the [discord.py](https://discordpy.readthedocs.io/en/stable/) library, which provides an easy-to-use interface for building bots that interact with Discord. It uses Discord's `Embed` system to format messages, as well as event-based commands to manage interactions in the server.


## Acknowledgements

- Thanks to the [Root Me](https://api.www.root-me.org/) platform for providing a comprehensive platform to learn and practice cybersecurity skills.
- Special thanks to the creators and maintainers of [`discord.py`](https://discordpy.readthedocs.io/en/stable/), the framework used to build this bot.
