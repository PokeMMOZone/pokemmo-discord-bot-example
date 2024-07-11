import discord
from discord.ext import commands
import yaml
import json
from discord import Embed
from datetime import datetime

# Load configuration from config.yml
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

TOKEN = config["token"]
COMMAND_CHANNEL_ID = config["command_channel_id"]

intents = discord.Intents.default()
intents.message_content = True  # To read message content
intents.guilds = True  # To access guilds (servers)

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)


def get_pokemmo_day_and_time():
    """
    Returns the current in-game day and time for PokeMMO based on the real-world time.

    Real-world to game time conversion in PokeMMO:
    - 15 seconds of real time = 1 minute of game time
    - 6 hours of real time = 24 hours of game time

    Additionally, it includes the current in-game season, shoal cave tide based on the month and time,
    and roaming legendaries in Johto and Kanto.

    Returns:
    str: Current in-game day and time, season, shoal cave tide, and roaming legendaries in PokeMMO.
    """
    # Get the current real-world time (UTC)
    now = datetime.utcnow()

    # Calculate the total minutes passed since a known reference date (e.g., a recent Monday at midnight)
    reference_date = datetime(2023, 12, 4)  # This date should be a Monday in UTC
    delta = now - reference_date

    # Convert real-world minutes to game time minutes
    game_time_minutes = delta.total_seconds() / 15

    # Calculate the in-game hour, minute, and day
    game_hour = int(game_time_minutes // 60) % 24
    game_minute = int(game_time_minutes % 60)
    game_days_passed = int(game_time_minutes // (24 * 60))

    # Calculate the in-game weekday
    game_weekday = game_days_passed % 7

    # Map the weekday number to a day name
    days_of_week = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]
    in_game_day_name = days_of_week[game_weekday]

    # Determine the current season based on the real-world month
    months_to_seasons = {
        1: "Spring", 2: "Summer", 3: "Autumn", 4: "Winter",
        5: "Spring", 6: "Summer", 7: "Autumn", 8: "Winter",
        9: "Spring", 10: "Summer", 11: "Autumn", 12: "Winter"
    }
    current_season = months_to_seasons[now.month]

    # Determine the shoal cave tide based on the in-game time
    shoal_cave_tide = "Low" if 3 <= game_hour < 9 or 15 <= game_hour < 21 else "High"

    # Determine the roaming legendaries for Johto and Kanto
    johto_legendaries = ["Entei", "Suicune", "Raikou"]
    kanto_legendaries = ["Zapdos", "Moltres", "Articuno"]

    current_month = now.month
    johto_legendary = johto_legendaries[(current_month - 1) % 3]
    kanto_legendary = kanto_legendaries[(current_month - 1) % 3]

    return (
        f"Day: {in_game_day_name}, Time: {game_hour:02d}:{game_minute:02d}\n"
        f"Season: {current_season}\n"
        f"Shoal Cave Tide: {shoal_cave_tide}\n"
        f"Johto Roamer: {johto_legendary}\n"
        f"Kanto Roamer: {kanto_legendary}"
    )


# A decorator to check if the command was invoked in the correct channel
def in_command_channel():
    async def predicate(ctx):
        return ctx.message.channel.id == COMMAND_CHANNEL_ID
    return commands.check(predicate)


@bot.command(name="hello", aliases=["greetings", "hi"])
@in_command_channel()
async def hello_cmd(ctx):
    """Replies with a hello message."""
    await ctx.message.reply(f"Hello, {ctx.author.display_name}!")


@bot.command(name="time", aliases=["gametime"])
async def time_cmd(ctx):
    """Replies with the current in-game day and time in PokeMMO."""
    in_game_time = get_pokemmo_day_and_time()
    await ctx.message.reply(f"{in_game_time}")


@bot.command(name="commands")
@in_command_channel()
async def _commands(ctx):
    """Displays all the commands and their descriptions."""
    helptext = "Here are the available commands:\n"
    for command in bot.commands:
        helptext += f"!{command.name} : {command.help}\n"
    await ctx.message.reply(helptext)


@bot.command(name="pokemon", aliases=["p"])
@in_command_channel()
async def pokemon_cmd(ctx, name: str):
    """Provides information about a specific Pokémon."""
    try:
        # Load the Pokémon data from the JSON file
        with open("data/pokemon-data.json", "r") as file:
            pokemon_data = json.load(file)

        # Find the Pokémon by name
        pokemon_info = pokemon_data.get(name.lower())

        if pokemon_info:
            # Create an embed object for the response
            embed = Embed(
                title=pokemon_info["name"].title(), color=0x00FF00
            )  # You can change the color

            # Set the thumbnail of the embed to the front image
            embed.set_thumbnail(url=pokemon_info["sprites"]["front_default"])

            # Add fields to the embed
            embed.add_field(
                name="Types",
                value=", ".join(pokemon_info["types"]).title(),
                inline=False,
            )
            embed.add_field(
                name="Abilities",
                value=", ".join(
                    f"{ability['ability_name'].title()}"
                    + (" (Hidden)" if ability["is_hidden"] else "")
                    for ability in pokemon_info["abilities"]
                ),
                inline=False,
            )
            embed.add_field(
                name="Base Stats",
                value="\n".join(
                    f"**{stat['stat_name'].title()}**: {stat['base_stat']}"
                    for stat in pokemon_info["stats"]
                ),
                inline=False,
            )
            embed.add_field(
                name="Capture Rate",
                value=str(pokemon_info["capture_rate"]),
                inline=False,
            )
            # embed.add_field(
            #     name="Base Experience",
            #     value=str(pokemon_info["base_experience"]),
            #     inline=False,
            # )
            embed.add_field(
                name="Egg Groups",
                value=", ".join(pokemon_info["egg_groups"]).title(),
                inline=False,
            )
            # embed.add_field(
            #     name="Growth Rate",
            #     value=pokemon_info["growth_rate"].title(),
            #     inline=False,
            # )

            # Evolution Chain
            def get_evolution_chain(chain):
                # If there is no 'evolves_to' key or it's empty, return an empty string.
                if "evolves_to" not in chain or not chain["evolves_to"]:
                    return chain["species"]["name"].title()

                # Start with the current species name
                evolutions = [chain["species"]["name"].title()]

                # Iterate over all possible evolutions
                for evolution in chain["evolves_to"]:
                    # Recursively get the evolution chain for the next level
                    next_evolution = get_evolution_chain(evolution)
                    # Append the next evolution to the list
                    evolutions.append(next_evolution)

                # Join all the evolutions with arrows to show the path
                return " -> ".join(evolutions)

            evolution_chain = get_evolution_chain(
                pokemon_info["evolution_chain"]["chain"]
            )

            # Only add the 'Evolution Chain' field if there is an evolution chain
            if evolution_chain and evolution_chain != pokemon_info["name"].title():
                embed.add_field(
                    name="Evolution Chain",
                    value=evolution_chain,
                    inline=False,
                )

            # Send the embed as a reply to the invoking message
            await ctx.reply(embed=embed)
        else:
            await ctx.message.reply(
                "Pokémon not found. Please check the name and try again."
            )
    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.reply("Sorry, I couldn't fetch the Pokémon data.")


@bot.command(name="types", aliases=["type"])
@in_command_channel()
async def types_cmd(ctx, type_name: str):
    """Provides information about a specific Pokémon type or lists all types if 'all' is specified."""
    try:
        # Load the Pokémon type data from the JSON file
        with open("data/types-data.json", "r") as file:
            types_data = json.load(file)

        if (type_name.lower() == "all"):
            # List all Pokémon type names
            all_types = ", ".join(types_data.keys())
            await ctx.reply(f"All Types: {all_types}")
        else:
            # Find the type by name
            type_data = types_data.get(type_name.lower(), None)

            if type_data:
                # Create an embed object for the response
                embed = Embed(
                    title=f"Pokémon Type: {type_name.title()}", color=0x00FF00
                )

                # List the Pokémon in the type
                pokemon_list = ", ".join(
                    f"{pokemon['name']}" for pokemon in type_data["pokemon"]
                )
                embed.add_field(
                    name="Pokémon of this Type", value=pokemon_list, inline=False
                )

                # List the moves of the type
                moves_list = ", ".join(f"{move['name']}" for move in type_data["moves"])
                embed.add_field(
                    name="Moves of this Type", value=moves_list, inline=False
                )

                # Send the embed as a reply to the invoking message
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(
                    f"Pokémon Type '{type_name}' not found. Please check the name and try again."
                )
    except Exception as e:
        print(f"Error: {e}")
        await ctx.reply("Sorry, I couldn't fetch the Pokémon type data.")


@bot.command(name="tiers", aliases=["tier", "pvp"])
@in_command_channel()
async def tiers_cmd(ctx, tier_name: str):
    """Provides information about a specific PvP tier or lists all tiers if 'all' is specified."""
    try:
        # Load the PvP tier data from the JSON file
        with open("data/pvp-data.json", "r") as file:
            pvp_data = json.load(file)

        if (tier_name.lower() == "all"):
            # List all tier names
            all_tiers = ", ".join(pvp_data.keys())
            await ctx.reply(f"All Tiers: {all_tiers}")
        else:
            # Find the tier by name
            tier_info = pvp_data.get(tier_name.upper(), None)

            if tier_info:
                # Create an embed object for the response
                embed = Embed(title=f"PvP Tier: {tier_name.upper()}", color=0x00FF00)

                # List the Pokémon in the tier
                pokemon_list = ", ".join(
                    pokemon["name"].title().replace("-", " ") for pokemon in tier_info
                )
                embed.add_field(
                    name="Pokémon in this Tier", value=pokemon_list, inline=False
                )

                # Send the embed as a reply to the invoking message
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(
                    f"PvP Tier '{tier_name}' not found. Please check the name and try again."
                )
    except Exception as e:
        print(f"Error: {e}")
        await ctx.reply("Sorry, I couldn't fetch the PvP tier data.")


@bot.command(name="egggroup", aliases=["eg"])
@in_command_channel()
async def egggroup_cmd(ctx, group_name: str):
    """Provides information about a specific Egg Group or lists all Egg Groups if 'all' is specified."""
    try:
        # Load the Egg Group data from the JSON file
        with open("data/egg-groups-data.json", "r") as file:
            egg_groups_data = json.load(file)

        if (group_name.lower() == "all"):
            # List all Egg Group names
            all_groups = ", ".join(
                group["name"].title() for group in egg_groups_data.values()
            )
            await ctx.reply(f"All Egg Groups: {all_groups}")
        else:
            # Find the Egg Group by name
            egg_group_info = next(
                (
                    group
                    for group in egg_groups_data.values()
                    if group["name"].lower() == group_name.lower()
                ),
                None,
            )

            if egg_group_info:
                # Create an embed object for the response
                embed = Embed(
                    title=f"Egg Group: {egg_group_info['name'].title()}", color=0x00FF00
                )

                # List the Pokémon species in the Egg Group
                pokemon_list = ", ".join(
                    species["name"].title().replace("-", " ")
                    for species in egg_group_info["pokemon_species"]
                )
                embed.add_field(
                    name="Pokémon Species", value=pokemon_list, inline=False
                )

                # Send the embed as a reply to the invoking message
                await ctx.reply(embed=embed)
            else:
                await ctx.message.reply(
                    f"Egg Group '{group_name}' not found. Please check the name and try again."
                )
    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.reply("Sorry, I couldn't fetch the Egg Group data.")


@bot.command(name="eggmoves", aliases=["em"])
@in_command_channel()
async def egg_moves_cmd(ctx, pokemon: str):
    """Responds with egg moves and breeding chains for the specified Pokemon. (Limit 30 per move.)"""
    try:
        # Load the egg moves data from the JSON file within the command
        with open("data/egg-moves-data.json", "r") as file:
            egg_moves_data = json.load(file)

        pokemon = pokemon.lower()  # Convert to lowercase to match keys in the JSON file

        if pokemon in egg_moves_data:
            # Respond with moves and a maximum of 30 breed chains for each move
            for move, chains in egg_moves_data[pokemon].items():
                response = f"**{move}** (Limit 30):\n"
                for chain in chains[:30]:  # Limit to 30 chains
                    response += " -> ".join(chain) + "\n"
                await ctx.message.reply(response)
        else:
            await ctx.message.reply(f"No egg move data found for {pokemon}.")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.reply("Sorry, I couldn't fetch the egg moves data.")


@bot.command(name="locations", aliases=["l"])
@in_command_channel()
async def locations_cmd(ctx, name: str):
    """Provides information about locations where a specific Pokémon can be found."""
    try:
        # Load the location data from the JSON file
        with open("data/pokemon-data.json", "r") as file:
            pokemon_data = json.load(file)

        # Find the Pokémon by name
        pokemon_info = pokemon_data.get(name.lower())

        if pokemon_info and "location_area_encounters" in pokemon_info:
            locations = pokemon_info["location_area_encounters"]
            # Split the locations into chunks of 25
            location_chunks = [
                locations[i: i + 25] for i in range(0, len(locations), 25)
            ]

            for index, chunk in enumerate(location_chunks, start=1):
                embed = Embed(
                    title=f"Locations for {pokemon_info['name'].title()} (Part {index})",
                    color=0x00FF00,
                )

                location_text = "\n".join(
                    f"{location['location']} (Lvl {location['min_level']}-{location['max_level']}, {location['rarity']}%)"
                    for location in chunk
                )

                embed.add_field(name="Locations", value=location_text, inline=False)

                # Send each embed in a separate message
                await ctx.reply(embed=embed)

        else:
            await ctx.message.reply(f"No location data found for {name}.")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.reply("Sorry, I couldn't fetch the location data.")


@bot.command(name="learnmoves", aliases=["lm"])
@in_command_channel()
async def learnmoves_cmd(ctx, name: str):
    """Provides information about moves that a specific Pokémon can learn."""
    try:
        # Load the Pokémon data from the JSON file
        with open("data/pokemon-data.json", "r") as file:
            pokemon_data = json.load(file)

        # Find the Pokémon by name
        pokemon_info = pokemon_data.get(name.lower())

        if pokemon_info and "moves" in pokemon_info:
            # Split the moves into chunks of 40
            moves_chunks = [
                pokemon_info["moves"][i: i + 40]
                for i in range(0, len(pokemon_info["moves"]), 40)
            ]

            for moves in moves_chunks:
                # Create an embed object for the response
                embed = Embed(
                    title=f"Learnable Moves for {pokemon_info['name'].title()}",
                    color=0x00FF00,
                )

                moves_text = "\n".join(
                    (
                        f"{move['name'].title()} (Lvl {move['level']})"
                        if move["type"] == "level"
                        else f"{move['name'].title()} ({move['type'].title()})"
                    )
                    for move in moves
                )

                # Add field to embed
                embed.add_field(name="Moves", value=moves_text, inline=False)

                # Send the embed as a reply to the invoking message
                await ctx.reply(embed=embed)

        else:
            await ctx.message.reply(f"No move data found for {name}.")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.reply("Sorry, I couldn't fetch the learnable moves data.")


@bot.command(name="ability", aliases=["a"])
@in_command_channel()
async def ability_cmd(ctx, ability_name: str):
    """Provides information about a specific ability and Pokémon that can learn it."""
    try:
        # Load the ability data from the JSON file
        with open("data/abilities-data.json", "r") as file:
            abilities_data = json.load(file)

        # Find the ability by name
        ability_info = abilities_data.get(ability_name.lower())

        if ability_info:
            # Create an embed object for the response
            embed = Embed(
                title=f"Ability: {ability_info['name'].title()}", color=0x00FF00
            )

            # Add fields to the embed
            embed.add_field(name="Effect", value=ability_info["effect"], inline=False)

            # Send the embed as a reply to the invoking message
            await ctx.reply(embed=embed)

            # Split the Pokémon into chunks of 30
            pokemon_chunks = [
                ability_info["pokemon_with_ability"][i: i + 30]
                for i in range(0, len(ability_info["pokemon_with_ability"]), 30)
            ]

            for pokemon_chunk in pokemon_chunks:
                pokemon_names = ", ".join(
                    pokemon["name"].title() for pokemon in pokemon_chunk
                )
                await ctx.message.reply(
                    f"Pokémon with '{ability_info['name'].title()}' ability: {pokemon_names}"
                )

        else:
            await ctx.message.reply(
                f"Ability '{ability_name}' not found. Please check the name and try again."
            )

    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.reply("Sorry, I couldn't fetch the ability data.")


@bot.command(name="move", aliases=["m"])
@in_command_channel()
async def move_cmd(ctx, move_name: str):
    """Provides information about a specific move and Pokémon that can learn it."""
    try:
        # Load the move data from the JSON file
        with open("data/moves-data.json", "r") as file:
            moves_data = json.load(file)

        # Find the move by name
        move_info = moves_data.get(move_name.lower())

        if move_info:
            # Create an embed object for the response
            embed = Embed(title=f"Move: {move_info['name'].title()}", color=0x00FF00)

            # Add fields to the embed
            embed.add_field(name="Type", value=move_info["type"].title(), inline=True)
            embed.add_field(
                name="Damage Class",
                value=move_info["damage_class"].title(),
                inline=True,
            )
            embed.add_field(name="Power", value=str(move_info["power"]), inline=True)
            embed.add_field(name="PP", value=str(move_info["pp"]), inline=True)
            embed.add_field(
                name="Accuracy", value=str(move_info["accuracy"]), inline=True
            )
            embed.add_field(name="Effect", value=move_info["effect"], inline=False)

            # Send the embed as a reply to the invoking message
            await ctx.reply(embed=embed)

            # Split the Pokémon into chunks of 30
            pokemon_chunks = [
                move_info["learned_by_pokemon"][i: i + 30]
                for i in range(0, len(move_info["learned_by_pokemon"]), 30)
            ]

            for pokemon_chunk in pokemon_chunks:
                pokemon_names = ", ".join(
                    pokemon["name"].title() for pokemon in pokemon_chunk
                )
                await ctx.message.reply(
                    f"Pokémon that can learn '{move_info['name'].title()}': {pokemon_names}"
                )

        else:
            await ctx.message.reply(
                f"Move '{move_name}' not found. Please check the name and try again."
            )

    except Exception as e:
        print(f"Error: {e}")
        await ctx.message.reply("Sorry, I couldn't fetch the move data.")


bot.run(TOKEN)
