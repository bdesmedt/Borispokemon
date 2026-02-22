"""
Pokémon Doolhof-Parcours
========================
Navigeer jouw Pokémon door een gegenereerd doolhof.
• Gebruik de pijlknoppen om te bewegen (omhoog/omlaag/links/rechts)
• Gevaarlijke vakjes kosten een leven (🔥 vuur, 💧 water, 🪨 rots)
• Bonusvakjes geven een extra leven terug (⭐)
• Bereik de finish 🏁 om te winnen!
"""
import streamlit as st
import random
from utils.styles import inject_custom_css
from utils.pokemon_data import POKEMON, POKEMON_IDS, sprite_url
from utils.caught_pokemon import mark_caught

st.set_page_config(page_title="Pokémon Doolhof", page_icon="🗺️", layout="wide")
inject_custom_css()

# ── constants ──────────────────────────────────────────────────────────────────
ROWS, COLS = 9, 9          # must be odd for maze generator
MAX_LIVES  = 5
HAZARD_PROB  = 0.08        # chance a free cell becomes a hazard
BONUS_PROB   = 0.10        # chance a free cell becomes a bonus

CELL_WALL    = "wall"
CELL_FREE    = "free"
CELL_HAZARD  = "hazard"
CELL_BONUS   = "bonus"
CELL_START   = "start"
CELL_FINISH  = "finish"

HAZARDS = ["🔥", "💧", "🪨", "⚡", "🌵"]

CELL_EMOJI = {
    CELL_WALL:   "⬛",
    CELL_FREE:   "⬜",
    CELL_HAZARD: None,   # filled per cell with hazard emoji
    CELL_BONUS:  "⭐",
    CELL_START:  "🟩",
    CELL_FINISH: "🏁",
}

# ── maze generation (randomised DFS) ──────────────────────────────────────────

def _generate_maze(rows: int, cols: int) -> list[list[str]]:
    """Return a grid of CELL_WALL / CELL_FREE using recursive backtracking."""
    grid = [[CELL_WALL] * cols for _ in range(rows)]

    def carve(r: int, c: int):
        grid[r][c] = CELL_FREE
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == CELL_WALL:
                grid[r + dr // 2][c + dc // 2] = CELL_FREE
                carve(nr, nc)

    carve(0, 0)
    return grid


def new_maze(pokemon_id: int | None = None):
    pid = pokemon_id or random.choice(POKEMON_IDS)
    grid = _generate_maze(ROWS, COLS)

    # Place hazards and bonuses on free cells (avoid start & finish corners)
    hazard_map: dict[tuple, str] = {}
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == CELL_FREE and (r, c) not in ((0, 0), (ROWS-1, COLS-1)):
                roll = random.random()
                if roll < HAZARD_PROB:
                    grid[r][c] = CELL_HAZARD
                    hazard_map[(r, c)] = random.choice(HAZARDS)
                elif roll < HAZARD_PROB + BONUS_PROB:
                    grid[r][c] = CELL_BONUS

    grid[0][0]              = CELL_START
    grid[ROWS-1][COLS-1]    = CELL_FINISH

    st.session_state.mz_grid       = grid
    st.session_state.mz_hazard_map = hazard_map
    st.session_state.mz_pokemon_id = pid
    st.session_state.mz_pos        = (0, 0)
    st.session_state.mz_visited    = {(0, 0)}
    st.session_state.mz_lives      = MAX_LIVES
    st.session_state.mz_steps      = 0
    st.session_state.mz_over       = False
    st.session_state.mz_won        = False
    st.session_state.mz_message    = ""


def try_move(dr: int, dc: int):
    r, c = st.session_state.mz_pos
    nr, nc = r + dr, c + dc
    grid = st.session_state.mz_grid

    if not (0 <= nr < ROWS and 0 <= nc < COLS):
        st.session_state.mz_message = "⛔ Buiten het doolhof!"
        return
    if grid[nr][nc] == CELL_WALL:
        st.session_state.mz_message = "🧱 Dat is een muur!"
        return

    st.session_state.mz_pos = (nr, nc)
    st.session_state.mz_visited.add((nr, nc))
    st.session_state.mz_steps += 1
    cell = grid[nr][nc]

    if cell == CELL_HAZARD:
        emoji = st.session_state.mz_hazard_map.get((nr, nc), "⚠️")
        st.session_state.mz_lives -= 1
        st.session_state.mz_message = f"{emoji} Au! Je raakte een gevaar en verliest een leven!"
        if st.session_state.mz_lives <= 0:
            st.session_state.mz_over = True
            st.session_state.mz_won  = False
            return
        # Replace hazard with free so it can be crossed safely next time
        grid[nr][nc] = CELL_FREE

    elif cell == CELL_BONUS:
        st.session_state.mz_lives = min(MAX_LIVES + 1, st.session_state.mz_lives + 1)
        st.session_state.mz_message = "⭐ Bonus! Je krijgt een extra leven!"
        grid[nr][nc] = CELL_FREE

    elif cell == CELL_FINISH:
        st.session_state.mz_over = True
        st.session_state.mz_won  = True
        mark_caught(st.session_state.mz_pokemon_id)
        return

    else:
        st.session_state.mz_message = ""


# ── init ───────────────────────────────────────────────────────────────────────
if "mz_grid" not in st.session_state:
    new_maze()

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown("## 🗺️ Pokémon Doolhof")
st.caption("Navigeer jouw Pokémon van 🟩 start naar 🏁 finish!")

pid  = st.session_state.mz_pokemon_id
name = POKEMON[pid]

# Header row: sprite + stats
col_sprite, col_stats = st.columns([1, 3])
with col_sprite:
    st.image(sprite_url(pid), width=100, caption=name)
with col_stats:
    lives_str = "❤️ " * st.session_state.mz_lives + "🖤 " * max(0, max(MAX_LIVES, st.session_state.mz_lives) - st.session_state.mz_lives)
    st.markdown(f"**Levens:** {lives_str}")
    st.markdown(f"**Stappen:** {st.session_state.mz_steps}")
    if st.session_state.mz_message:
        st.info(st.session_state.mz_message)

st.markdown("---")

# ── render grid ────────────────────────────────────────────────────────────────
if not st.session_state.mz_over:
    pr, pc  = st.session_state.mz_pos
    grid    = st.session_state.mz_grid
    hmap    = st.session_state.mz_hazard_map
    visited = st.session_state.mz_visited

    rows_html = ""
    for r in range(ROWS):
        row_html = "<tr>"
        for c in range(COLS):
            if (r, c) == (pr, pc):
                cell_content = f'<img src="{sprite_url(pid)}" width="36" style="image-rendering:pixelated;"/>'
                bg = "#c8e6c9"
            else:
                ctype = grid[r][c]
                if ctype == CELL_WALL:
                    cell_content = "⬛"
                    bg = "#333"
                elif ctype == CELL_HAZARD:
                    cell_content = hmap.get((r, c), "⚠️")
                    bg = "#fff3e0"
                elif ctype == CELL_BONUS:
                    cell_content = "⭐"
                    bg = "#fffde7"
                elif ctype == CELL_FINISH:
                    cell_content = "🏁"
                    bg = "#e8f5e9"
                elif ctype == CELL_START:
                    cell_content = "🟩"
                    bg = "#f1f8e9"
                else:
                    if (r, c) in visited:
                        cell_content = "·"
                        bg = "#dceeff"
                    else:
                        cell_content = ""
                        bg = "#fafafa"
            row_html += (
                f'<td style="width:42px;height:42px;text-align:center;vertical-align:middle;'
                f'background:{bg};border:1px solid #ddd;font-size:1.4rem;">'
                f'{cell_content}</td>'
            )
        row_html += "</tr>"
        rows_html += row_html

    st.markdown(
        f'<table style="border-collapse:collapse;margin:auto;">{rows_html}</table>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── direction controls ─────────────────────────────────────────────────────
    pad, up_col, _ = st.columns([2, 1, 2])
    with up_col:
        if st.button("⬆️", use_container_width=True, key="up"):
            try_move(-1, 0); st.rerun()

    left_col, _, right_col = st.columns([1, 1, 1])
    with left_col:
        if st.button("⬅️", use_container_width=True, key="left"):
            try_move(0, -1); st.rerun()
    with right_col:
        if st.button("➡️", use_container_width=True, key="right"):
            try_move(0, 1); st.rerun()

    pad2, down_col, _ = st.columns([2, 1, 2])
    with down_col:
        if st.button("⬇️", use_container_width=True, key="down"):
            try_move(1, 0); st.rerun()

else:
    if st.session_state.mz_won:
        st.success(f"🏆 Gefeliciteerd! **{name}** heeft het doolhof uitgelopen in **{st.session_state.mz_steps} stappen**!")
        st.info(f"🎉 **{name}** is toegevoegd aan je Pokédex!")
        st.balloons()
    else:
        st.error(f"💀 **{name}** heeft alle levens verloren. Probeer opnieuw!")
    if st.button("🔄 Nieuw doolhof", type="primary", use_container_width=True):
        new_maze(st.session_state.mz_pokemon_id)
        st.rerun()

# ── legenda ───────────────────────────────────────────────────────────────────
with st.expander("📖 Legenda"):
    st.markdown("""
| Symbool | Betekenis |
|---|---|
| 🟩 | Startpositie |
| 🏁 | Finish |
| ⬛ | Muur (niet doorheen) |
| ⬜ | Vrij pad |
| 🔥💧🪨⚡🌵 | Gevaar (-1 leven) |
| ⭐ | Bonus (+1 leven) |
""")

# ── sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Kies jouw Pokémon")
    chosen = st.selectbox("Pokémon", options=POKEMON_IDS, format_func=lambda i: POKEMON[i])
    if st.button("Start met deze Pokémon"):
        new_maze(pokemon_id=chosen)
        st.rerun()
    st.markdown("---")
    if st.button("🔄 Nieuw doolhof", use_container_width=True):
        new_maze(st.session_state.mz_pokemon_id)
        st.rerun()
