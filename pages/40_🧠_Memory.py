"""
Pokémon Memory
==============
Een klassiek memory-spel met Pokémon-sprites.
• Kies een moeilijkheidsgraad (4×2, 4×3 of 4×4 kaarten)
• Klik op twee kaarten om ze om te draaien
• Gevonden paren blijven zichtbaar
• Win als alle paren gevonden zijn
"""
import streamlit as st
import random
from utils.styles import inject_custom_css
from utils.pokemon_data import POKEMON, POKEMON_IDS, sprite_url
from utils.caught_pokemon import mark_caught

st.set_page_config(page_title="Pokémon Memory", page_icon="🧠", layout="wide")
inject_custom_css()

# ── difficulty presets ─────────────────────────────────────────────────────────
DIFFICULTIES = {
    "Makkelijk (4×2)":  {"pairs": 4,  "cols": 4},
    "Normaal (4×3)":    {"pairs": 6,  "cols": 4},
    "Moeilijk (4×4)":   {"pairs": 8,  "cols": 4},
}

CARD_BACK = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png"


def new_memory(difficulty: str):
    cfg   = DIFFICULTIES[difficulty]
    pairs = cfg["pairs"]
    cols  = cfg["cols"]

    chosen_ids = random.sample(POKEMON_IDS, pairs)
    card_ids   = chosen_ids * 2
    random.shuffle(card_ids)

    st.session_state.m_cards     = card_ids          # list of pokemon_id per card
    st.session_state.m_flipped   = [False] * len(card_ids)
    st.session_state.m_matched   = [False] * len(card_ids)
    st.session_state.m_selected  = []               # indices currently face-up (max 2)
    st.session_state.m_attempts  = 0
    st.session_state.m_pairs_found = 0
    st.session_state.m_total_pairs = pairs
    st.session_state.m_cols      = cols
    st.session_state.m_difficulty = difficulty
    st.session_state.m_over      = False
    st.session_state.m_mismatch  = False            # show mismatch feedback


# ── init ───────────────────────────────────────────────────────────────────────
if "m_cards" not in st.session_state:
    new_memory("Normaal (4×3)")

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown("## 🧠 Pokémon Memory")
st.caption("Vind alle overeenkomende Pokémon-paren!")

# Stats row
s1, s2, s3, s4 = st.columns(4)
s1.metric("Paren gevonden", f"{st.session_state.m_pairs_found}/{st.session_state.m_total_pairs}")
s2.metric("Pogingen", st.session_state.m_attempts)
if st.session_state.m_attempts > 0:
    acc = st.session_state.m_pairs_found / st.session_state.m_attempts * 100
    s3.metric("Nauwkeurigheid", f"{acc:.0f}%")
else:
    s3.metric("Nauwkeurigheid", "–")
s4.metric("Moeilijkheid", st.session_state.m_difficulty.split(" ")[0])

st.markdown("---")

# ── mismatch feedback (shown for one render cycle) ─────────────────────────────
if st.session_state.m_mismatch:
    sel = st.session_state.m_selected
    if len(sel) == 2:
        n1 = POKEMON[st.session_state.m_cards[sel[0]]]
        n2 = POKEMON[st.session_state.m_cards[sel[1]]]
        st.warning(f"❌ Geen match: **{n1}** en **{n2}** — kaarten worden teruggedraaid.")
    # Flip back
    for idx in st.session_state.m_selected:
        st.session_state.m_flipped[idx] = False
    st.session_state.m_selected = []
    st.session_state.m_mismatch = False

# ── card grid ──────────────────────────────────────────────────────────────────
cards   = st.session_state.m_cards
flipped = st.session_state.m_flipped
matched = st.session_state.m_matched
n_cols  = st.session_state.m_cols

if not st.session_state.m_over:
    for row_start in range(0, len(cards), n_cols):
        row_cards = list(range(row_start, min(row_start + n_cols, len(cards))))
        cols = st.columns(len(row_cards))
        for col, idx in zip(cols, row_cards):
            pid = cards[idx]
            with col:
                if matched[idx]:
                    # Permanently revealed
                    st.image(sprite_url(pid), width=90)
                    st.markdown(
                        f"<p style='text-align:center;font-size:0.7rem;color:#4caf50;'>"
                        f"✅ {POKEMON[pid]}</p>",
                        unsafe_allow_html=True,
                    )
                elif flipped[idx]:
                    # Currently face-up (selected)
                    st.image(sprite_url(pid), width=90)
                    st.markdown(
                        f"<p style='text-align:center;font-size:0.7rem;color:#ff9800;'>"
                        f"❓ {POKEMON[pid]}</p>",
                        unsafe_allow_html=True,
                    )
                else:
                    # Face-down card: show pokeball button
                    if st.button("🔵", key=f"card_{idx}", use_container_width=True,
                                 help="Klik om om te draaien"):
                        # Only allow if fewer than 2 cards are selected
                        if len(st.session_state.m_selected) < 2 and not st.session_state.m_mismatch:
                            st.session_state.m_flipped[idx] = True
                            st.session_state.m_selected.append(idx)

                            if len(st.session_state.m_selected) == 2:
                                i1, i2 = st.session_state.m_selected
                                st.session_state.m_attempts += 1
                                if cards[i1] == cards[i2]:
                                    # Match!
                                    st.session_state.m_matched[i1] = True
                                    st.session_state.m_matched[i2] = True
                                    st.session_state.m_selected = []
                                    st.session_state.m_pairs_found += 1
                                    mark_caught(cards[i1])
                                    if st.session_state.m_pairs_found >= st.session_state.m_total_pairs:
                                        st.session_state.m_over = True
                                else:
                                    st.session_state.m_mismatch = True
                        st.rerun()
else:
    attempts = st.session_state.m_attempts
    pairs    = st.session_state.m_total_pairs
    st.success(f"🏆 Gefeliciteerd! Je hebt alle **{pairs} paren** gevonden in **{attempts} pogingen**!")
    st.balloons()

st.markdown("---")

# ── controls ───────────────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 1])
with c1:
    diff = st.selectbox("Moeilijkheidsgraad", list(DIFFICULTIES.keys()),
                        index=list(DIFFICULTIES.keys()).index(st.session_state.m_difficulty))
with c2:
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Nieuw spel", type="primary", use_container_width=True):
        new_memory(diff)
        st.rerun()
