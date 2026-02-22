"""
Parcours — ontwijkspel
======================
De Pokémon rent over een parcours van 10 vakjes.
Op elk vakje kunnen gevaarlijke objecten verschijnen (links, midden, rechts).
De speler kiest elke stap: ga naar Links, Midden of Rechts.
Raak je een object → je verliest een leven.
Haal je het einde → je wint!
"""
import streamlit as st
import random
from utils.styles import inject_custom_css
from utils.pokemon_data import POKEMON, POKEMON_IDS, sprite_url

st.set_page_config(page_title="Pokémon Parcours", page_icon="🏃", layout="wide")
inject_custom_css()

# ── constants ──────────────────────────────────────────────────────────────────
TRACK_LENGTH = 10
MAX_LIVES    = 3
LANES        = ["⬅️ Links", "⬆️ Midden", "➡️ Rechts"]
LANE_KEYS    = ["links", "midden", "rechts"]

OBSTACLES = ["🪨 Rots", "🔥 Vuur", "💧 Waterplas", "⚡ Bliksem", "🌪️ Wervelwind", "🌵 Cactus"]

SAFE_EMOJI   = "✅"
HIT_EMOJI    = "💥"
EMPTY_EMOJI  = "⬜"
OBSTACLE_EMOJI = "🚧"


def generate_step() -> dict:
    """Return a dict with the obstacle layout for one step."""
    num_obstacles = random.choices([1, 2], weights=[70, 30])[0]
    blocked_lanes = random.sample(LANE_KEYS, num_obstacles)
    obstacle_type = {lane: random.choice(OBSTACLES) for lane in blocked_lanes}
    return {"blocked": blocked_lanes, "obstacle_type": obstacle_type}


def new_parcours(pokemon_id: int | None = None):
    pid = pokemon_id or random.choice(POKEMON_IDS)
    st.session_state.p_pokemon_id = pid
    st.session_state.p_step       = 0          # current position (0 = start)
    st.session_state.p_lives      = MAX_LIVES
    st.session_state.p_lane       = "midden"   # starting lane
    st.session_state.p_history    = []          # list of step result dicts
    st.session_state.p_over       = False
    st.session_state.p_won        = False
    # Pre-generate all obstacle steps
    st.session_state.p_track = [generate_step() for _ in range(TRACK_LENGTH)]


def draw_track():
    """Render the parcours track as a visual grid."""
    step = st.session_state.p_step
    history = st.session_state.p_history
    track = st.session_state.p_track

    cols = st.columns(TRACK_LENGTH + 1)
    cols[0].markdown("**Stap**")
    for i in range(TRACK_LENGTH):
        label = f"**{i+1}**"
        if i < step:
            result = history[i]
            icon = HIT_EMOJI if result["hit"] else SAFE_EMOJI
            cols[i+1].markdown(f"{icon}")
        elif i == step and not st.session_state.p_over:
            cols[i+1].markdown("🏃")
        else:
            cols[i+1].markdown(EMPTY_EMOJI)


# ── init ───────────────────────────────────────────────────────────────────────
if "p_pokemon_id" not in st.session_state:
    new_parcours()

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown("## 🏃 Pokémon Parcours")
st.caption("Ontwijkt gevaarlijke objecten en bereik het einde!")

pid  = st.session_state.p_pokemon_id
name = POKEMON[pid]

col_sprite, col_info = st.columns([1, 3])
with col_sprite:
    st.image(sprite_url(pid), width=120, caption=name)
with col_info:
    lives_display = "❤️ " * st.session_state.p_lives + "🖤 " * (MAX_LIVES - st.session_state.p_lives)
    st.markdown(f"**Levens:** {lives_display}")
    pct = st.session_state.p_step / TRACK_LENGTH * 100
    st.progress(int(pct), text=f"Stap {st.session_state.p_step}/{TRACK_LENGTH}")

st.markdown("---")
draw_track()
st.markdown("---")

# ── game logic ─────────────────────────────────────────────────────────────────
if not st.session_state.p_over:
    current_step = st.session_state.p_track[st.session_state.p_step]
    blocked      = current_step["blocked"]
    obs_types    = current_step["obstacle_type"]

    st.markdown("### Wat zit er op dit vakje?")
    c1, c2, c3 = st.columns(3)
    for col, lane_key, lane_label in zip([c1, c2, c3], LANE_KEYS, LANES):
        if lane_key in blocked:
            col.markdown(f"**{obs_types[lane_key]}**")
        else:
            col.markdown("🟢 Vrij")

    st.markdown("### Kies jouw rijstrook:")
    bc1, bc2, bc3 = st.columns(3)
    chosen_lane = None
    if bc1.button(LANES[0], use_container_width=True, key="btn_links"):
        chosen_lane = "links"
    if bc2.button(LANES[1], use_container_width=True, key="btn_midden"):
        chosen_lane = "midden"
    if bc3.button(LANES[2], use_container_width=True, key="btn_rechts"):
        chosen_lane = "rechts"

    if chosen_lane is not None:
        hit = chosen_lane in blocked
        st.session_state.p_history.append({
            "step": st.session_state.p_step + 1,
            "lane": chosen_lane,
            "hit": hit,
            "obstacle": obs_types.get(chosen_lane, None),
        })
        if hit:
            st.session_state.p_lives -= 1
        st.session_state.p_step += 1
        st.session_state.p_lane = chosen_lane

        if st.session_state.p_lives <= 0:
            st.session_state.p_over = True
            st.session_state.p_won  = False
        elif st.session_state.p_step >= TRACK_LENGTH:
            st.session_state.p_over = True
            st.session_state.p_won  = True
        st.rerun()

else:
    if st.session_state.p_won:
        st.success(f"🏆 Gefeliciteerd! **{name}** heeft het parcours voltooid!")
        st.balloons()
    else:
        st.error(f"💀 **{name}** heeft alle levens verloren. Probeer opnieuw!")

    if st.button("🔄 Nieuw parcours", type="primary", use_container_width=True):
        new_parcours(st.session_state.p_pokemon_id)
        st.rerun()

# ── history ────────────────────────────────────────────────────────────────────
if st.session_state.p_history:
    st.markdown("### 📋 Jouw parcours")
    for entry in st.session_state.p_history:
        icon = HIT_EMOJI if entry["hit"] else SAFE_EMOJI
        lane_nl = {"links": "Links", "midden": "Midden", "rechts": "Rechts"}[entry["lane"]]
        obs_txt = f" — raak: **{entry['obstacle']}**" if entry["hit"] else ""
        st.markdown(f"{icon} Stap {entry['step']}: **{lane_nl}**{obs_txt}")

# ── sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Kies jouw Pokémon")
    chosen = st.selectbox("Pokémon", options=POKEMON_IDS, format_func=lambda i: POKEMON[i])
    if st.button("Start met deze Pokémon"):
        new_parcours(pokemon_id=chosen)
        st.rerun()
