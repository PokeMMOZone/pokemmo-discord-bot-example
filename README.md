# PokeMMO Discord Bot Example

This repository contains an example of a PokeMMO Discord bot that anyone can use. It demonstrates how to utilize the [PokeMMO-Data](https://github.com/PokeMMOZone/PokeMMO-Data) library to provide various commands related to PokeMMO. The data used by the bot is located in the `data` folder.

## Features

- Fetch current in-game day and time for PokeMMO.
- Retrieve information about specific Pokémon.
- List available commands.
- Provide details about Pokémon types, PvP tiers, egg groups, egg moves, locations, learnable moves, abilities, and specific moves.

## Installation

### Prerequisites

- Python 3.8 or higher
- Discord bot token
- [PokeMMO-Data](https://github.com/PokeMMOZone/PokeMMO-Data)

### Steps

1. Clone the repository:

    ```sh
    git clone https://github.com/PokeMMOZone/pokemmo-discord-bot-example.git
    cd pokemmo-discord-bot-example
    ```

2. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

3. Configure the bot:

    - Copy the sample configuration file and rename it to `config.yml`:

        ```sh
        cp config.yml.sample config.yml
        ```

    - Edit `config.yml` to include your Discord bot token and the appropriate channel ID where the bot should listen for commands.

4. Run the bot:

    ```sh
    python run.py
    ```

## Configuration

The `config.yml` file should contain the following:

```yaml
token: "YOUR_DISCORD_BOT_TOKEN"
command_channel_id: YOUR_COMMAND_CHANNEL_ID
```

## Commands

### `!hello`, `!greetings`, `!hi`

Replies with a hello message.

### `!time`, `!gametime`

Replies with the current in-game day and time in PokeMMO.

### `!commands`

Displays all the available commands and their descriptions.

### `!pokemon <name>`, `!p <name>`

Provides information about a specific Pokémon.

### `!types <type_name>`, `!type <type_name>`

Provides information about a specific Pokémon type or lists all types if 'all' is specified.

### `!tiers <tier_name>`, `!tier <tier_name>`, `!pvp <tier_name>`

Provides information about a specific PvP tier or lists all tiers if 'all' is specified.

### `!egggroup <group_name>`, `!eg <group_name>`

Provides information about a specific Egg Group or lists all Egg Groups if 'all' is specified.

### `!eggmoves <pokemon>`, `!em <pokemon>`

Responds with egg moves and breeding chains for the specified Pokémon. (Limit 30 per move.)

### `!locations <name>`, `!l <name>`

Provides information about locations where a specific Pokémon can be found.

### `!learnmoves <name>`, `!lm <name>`

Provides information about moves that a specific Pokémon can learn.

### `!ability <ability_name>`, `!a <ability_name>`

Provides information about a specific ability and Pokémon that can learn it.

### `!move <move_name>`, `!m <move_name>`

Provides information about a specific move and Pokémon that can learn it.

## Data Source

The data used by this bot is sourced from the [PokeMMO-Data](https://github.com/PokeMMOZone/PokeMMO-Data) project. Make sure to keep the data in the `data` folder up to date with the latest data from the PokeMMO-Data repository.

## Contributing

Feel free to open issues or pull requests if you find any bugs or have suggestions for improvements.

## License

This project is licensed under the GNU General Public License v2.0. See the [LICENSE](./LICENSE) file for more details.
