import streamlit as st
import random
from utils.styles import inject_custom_css
from utils.caught_pokemon import mark_caught

st.set_page_config(page_title="Wie is dat Pokemon? - Kookrooster", page_icon="🎮", layout="wide")
inject_custom_css()

SPRITE_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png"
SPRITE_SHINY = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{id}.png"

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

pokemon_ids = list(POKEMON.keys())
pokemon_names = list(POKEMON.values())

# ── Session state ──────────────────────────────────────────────────────────────
if "pokemon_id" not in st.session_state:
    st.session_state.pokemon_id = random.choice(pokemon_ids)
if "revealed" not in st.session_state:
    st.session_state.revealed = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = None  # "correct" | "wrong" | None
if "wrong_answer" not in st.session_state:
    st.session_state.wrong_answer = None

def new_pokemon():
    st.session_state.pokemon_id = random.choice(pokemon_ids)
    st.session_state.revealed = False
    st.session_state.feedback = None
    st.session_state.wrong_answer = None

def check_answer(guess: str):
    correct = POKEMON[st.session_state.pokemon_id]
    st.session_state.total += 1
    if guess.strip().lower() == correct.lower():
        st.session_state.score += 1
        st.session_state.streak += 1
        st.session_state.feedback = "correct"
        mark_caught(st.session_state.pokemon_id)
    else:
        st.session_state.streak = 0
        st.session_state.feedback = "wrong"
        st.session_state.wrong_answer = guess
    st.session_state.revealed = True

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown("## 🎮 Wie is dat Pokémon?")
st.caption("Raad de Pokémon op basis van zijn silhouet!")

# Score bar
col_sc1, col_sc2, col_sc3 = st.columns(3)
col_sc1.metric("Score", f"{st.session_state.score} / {st.session_state.total}")
col_sc2.metric("Streak", f"🔥 {st.session_state.streak}")
if st.session_state.total > 0:
    col_sc3.metric("Nauwkeurigheid", f"{st.session_state.score / st.session_state.total * 100:.0f}%")
else:
    col_sc3.metric("Nauwkeurigheid", "–")

st.markdown("---")

pid = st.session_state.pokemon_id
sprite_url = SPRITE_BASE.format(id=pid)
correct_name = POKEMON[pid]

# Sprite display
col_img, col_game = st.columns([1, 2])

with col_img:
    if st.session_state.revealed:
        st.image(sprite_url, width=220, caption=correct_name)
    else:
        # Show silhouette using CSS filter
        st.markdown(
            f"""
            <div style="text-align:center;">
                <img src="{sprite_url}"
                     width="220"
                     style="filter: brightness(0); image-rendering: pixelated;"
                     alt="Wie is dat Pokémon?" />
                <p style="color:#888;font-size:0.85rem;margin-top:0.4rem;">Wie is dat Pokémon?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_game:
    if st.session_state.revealed:
        # Feedback
        if st.session_state.feedback == "correct":
            st.success(f"✅ Goed! Het is **{correct_name}**!")
            st.info(f"🎉 **{correct_name}** is toegevoegd aan je Pokédex!")
        elif st.session_state.feedback == "wrong":
            st.error(f"❌ Fout! Je raadde **{st.session_state.wrong_answer}**, maar het was **{correct_name}**.")

        if st.button("➡️ Volgende Pokémon", type="primary", use_container_width=True):
            new_pokemon()
            st.rerun()
    else:
        # Multiple choice: correct + 3 random wrong answers
        choices = [correct_name]
        wrong_pool = [n for n in pokemon_names if n != correct_name]
        choices += random.sample(wrong_pool, 3)
        random.shuffle(choices)

        st.markdown("### Wat is dit Pokémon?")
        cols = st.columns(2)
        for i, choice in enumerate(choices):
            with cols[i % 2]:
                if st.button(choice, key=f"choice_{choice}", use_container_width=True):
                    check_answer(choice)
                    st.rerun()

        st.markdown("---")
        if st.button("🔍 Onthullen (overslaan)", use_container_width=True):
            st.session_state.revealed = True
            st.session_state.total += 1
            st.session_state.streak = 0
            st.session_state.feedback = "wrong"
            st.session_state.wrong_answer = "(overgeslagen)"
            st.rerun()

# Reset
st.markdown("---")
if st.button("🔄 Reset Score"):
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.total = 0
    new_pokemon()
    st.rerun()
