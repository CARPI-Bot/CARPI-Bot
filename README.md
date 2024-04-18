# CARPI Bot

The Discord bot built for RPI students! Featuring an in-app academic calendar menu, easy search of the course catalog, as well as access to other RPI resources from within the popular messaging app, we hope that our bot will be a friend to you in your everyday academic endeavors.

## User Quick Start

**1. Discord Account** \
As CARPI Bot operates on the social & messaging platform Discord, you'll need to [create an account](https://discord.com/ "Click to redirect!") to use it if you haven't already.

**2. Add CARPI Bot to Your Discord Server** \
Once you're ready, use this [invite link](https://discord.com/oauth2/authorize?client_id=1067560443444478034&permissions=8&scope=bot+applications.commands "Click to invite CARPI Bot to a server!") to add CARPI Bot to your server! You must have the `Manage Server` permission within the server you want to invite the bot to.

**3. Start using commands** \
Once CARPI Bot is in your server, all of its commands are at your disposal! Use the `/help` command to see a list of comands.

## Getting started with contributing
### Project Dependencies

**Python (3.9+)**
> [Download Python](https://www.python.org "Click to redirect!")

**MySQL Server (8.2.0)**
> [Download MySQL Server](https://dev.mysql.com/downloads/mysql "Click to redirect!")

**Python PIP packages:**
> discord.py \
> aiomysql \
> aiohttp \
> cryptography

These can be installed using `pip install -r requirements.txt`

### Required configuration
Because of sensitive credentials like Discord bot tokens and database logins, this project depends on a `config.json` placed in `src`. The structure of the file is as follows:
```
{
    "token": "discord_bot_token",
    "prefix": "command_prefix",
    "sql_login":
        {
            "host": "hostname",
            "port": 0000,
            "user": "username",
            "password": "password"
        },
    "sql_schema": "schema_name"
}
```

## Contributors

Raymond Chen    '26 \
Miranda Zheng   '26 \
Kai Wang        '26 \
Gavin Liu       '26 \
Justin Isaac    '26 \
Brian Wang-Chen '25 \
Alex Montes     '23 \
Anthony Smith   '27 \
Julian Rosario  '26 \
Ryan So         '26 \
Florence Wang   '26 \
Edwin Zhao      '26 \
Jack Zgombic    '26
