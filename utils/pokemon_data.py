POKEMON = {
    1: "Bulbasaur", 2: "Ivysaur", 3: "Venusaur", 4: "Charmander", 5: "Charmeleon",
    6: "Charizard", 7: "Squirtle", 8: "Wartortle", 9: "Blastoise", 10: "Caterpie",
    11: "Metapod", 12: "Butterfree", 13: "Weedle", 14: "Kakuna", 15: "Beedrill",
    16: "Pidgey", 17: "Pidgeotto", 18: "Pidgeot", 19: "Rattata", 20: "Raticate",
    25: "Pikachu", 26: "Raichu", 35: "Clefairy", 36: "Clefable", 37: "Vulpix",
    38: "Ninetales", 39: "Jigglypuff", 40: "Wigglytuff", 50: "Diglett", 51: "Dugtrio",
    52: "Meowth", 53: "Persian", 54: "Psyduck", 55: "Golduck", 56: "Mankey",
    57: "Primeape", 58: "Growlithe", 59: "Arcanine", 60: "Poliwag", 61: "Poliwhirl",
    63: "Abra", 64: "Kadabra", 65: "Alakazam", 66: "Machop", 67: "Machoke",
    68: "Machamp", 74: "Geodude", 75: "Graveler", 76: "Golem", 77: "Ponyta",
    79: "Slowpoke", 80: "Slowbro", 81: "Magnemite", 82: "Magneton", 84: "Doduo",
    86: "Seel", 88: "Grimer", 90: "Shellder", 92: "Gastly", 93: "Haunter",
    94: "Gengar", 95: "Onix", 96: "Drowzee", 97: "Hypno", 98: "Krabby",
    100: "Voltorb", 101: "Electrode", 102: "Exeggcute", 103: "Exeggutor",
    104: "Cubone", 105: "Marowak", 106: "Hitmonlee", 107: "Hitmonchan",
    108: "Lickitung", 109: "Koffing", 110: "Weezing", 111: "Rhyhorn",
    112: "Rhydon", 113: "Chansey", 114: "Tangela", 115: "Kangaskhan",
    116: "Horsea", 117: "Seadra", 118: "Goldeen", 119: "Seaking",
    120: "Staryu", 121: "Starmie", 122: "Mr. Mime", 123: "Scyther",
    124: "Jynx", 125: "Electabuzz", 126: "Magmar", 127: "Pinsir",
    128: "Tauros", 129: "Magikarp", 130: "Gyarados", 131: "Lapras",
    132: "Ditto", 133: "Eevee", 134: "Vaporeon", 135: "Jolteon",
    136: "Flareon", 137: "Porygon", 138: "Omanyte", 139: "Omastar",
    140: "Kabuto", 141: "Kabutops", 142: "Aerodactyl", 143: "Snorlax",
    144: "Articuno", 145: "Zapdos", 146: "Moltres", 147: "Dratini",
    148: "Dragonair", 149: "Dragonite", 150: "Mewtwo", 151: "Mew",
}

SPRITE_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png"
SPRITE_BACK = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/{id}.png"

POKEMON_IDS = list(POKEMON.keys())
POKEMON_NAMES = list(POKEMON.values())


def get_stats(pokemon_id: int) -> dict:
    """Derive simple battle stats from the Pokemon ID (deterministic)."""
    seed = pokemon_id * 37
    hp      = 40 + (seed % 61)          # 40–100
    attack  = 30 + ((seed // 3) % 71)   # 30–100
    defense = 20 + ((seed // 7) % 61)   # 20–80
    speed   = 20 + ((seed // 11) % 61)  # 20–80
    return {"hp": hp, "attack": attack, "defense": defense, "speed": speed}


def sprite_url(pokemon_id: int) -> str:
    return SPRITE_BASE.format(id=pokemon_id)


def back_sprite_url(pokemon_id: int) -> str:
    return SPRITE_BACK.format(id=pokemon_id)
