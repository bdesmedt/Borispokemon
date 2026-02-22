"""
Pokédex — gevangen Pokémon
==========================
Overzicht van alle Pokémon die je hebt gevangen via de andere spellen:
  • Wie is dat Pokémon? → vang bij juist geraden antwoord
  • Gevechtsspel       → vang de tegenstander bij winst
  • Parcours           → vang je Pokémon bij het voltooien van het parcours
  • Memory             → vang elk gevonden paar
"""
import streamlit as st
from utils.styles import inject_custom_css
from utils.pokemon_data import POKEMON, POKEMON_IDS, sprite_url
from utils.caught_pokemon import load_caught, reset_caught

st.set_page_config(page_title="Pokédex", page_icon="📋", layout="wide")
inject_custom_css()

st.markdown("## 📋 Jouw Pokédex")
st.caption("Alle Pokémon die je hebt gevangen via de verschillende spellen.")

caught = load_caught()
total_species = len(caught)
total_catches = sum(caught.values())
total_possible = len(POKEMON_IDS)

# ── summary stats ──────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Soorten gevangen", f"{total_species} / {total_possible}")
c2.metric("Totaal gevangen", total_catches)
c3.metric("Completie", f"{total_species / total_possible * 100:.0f}%")

st.progress(total_species / total_possible)

st.markdown("---")

if not caught:
    st.info("Je hebt nog geen Pokémon gevangen. Speel de andere spellen om ze te vangen!")
else:
    # ── filter & sort controls ─────────────────────────────────────────────────
    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Zoek op naam", placeholder="bijv. Pikachu")
    with col_sort:
        sort_by = st.selectbox("Sorteren op", ["Pokédex #", "Naam", "Meest gevangen"])

    # Build display list
    display = [(pid, POKEMON[pid], caught[pid]) for pid in caught if pid in POKEMON]

    if search:
        display = [(pid, name, cnt) for pid, name, cnt in display
                   if search.lower() in name.lower()]

    if sort_by == "Naam":
        display.sort(key=lambda x: x[1])
    elif sort_by == "Meest gevangen":
        display.sort(key=lambda x: x[2], reverse=True)
    else:
        display.sort(key=lambda x: x[0])

    st.markdown(f"**{len(display)} Pokémon gevonden**")
    st.markdown("---")

    # ── card grid ──────────────────────────────────────────────────────────────
    GRID_COLS = 6
    for row_start in range(0, len(display), GRID_COLS):
        row = display[row_start: row_start + GRID_COLS]
        cols = st.columns(GRID_COLS)
        for col, (pid, name, cnt) in zip(cols, row):
            with col:
                st.image(sprite_url(pid), width=90)
                st.markdown(
                    f"<p style='text-align:center;font-size:0.75rem;margin:0;'>"
                    f"<strong>#{pid}</strong><br>{name}</p>"
                    f"<p style='text-align:center;font-size:0.7rem;color:#aaa;margin:0;'>"
                    f"x{cnt} gevangen</p>",
                    unsafe_allow_html=True,
                )

# ── not yet caught ─────────────────────────────────────────────────────────────
with st.expander("👻 Nog niet gevangen"):
    missing = [pid for pid in POKEMON_IDS if pid not in caught]
    if not missing:
        st.success("🏆 Je hebt alle Pokémon gevangen!")
    else:
        GRID_COLS = 6
        for row_start in range(0, len(missing), GRID_COLS):
            row = missing[row_start: row_start + GRID_COLS]
            cols = st.columns(GRID_COLS)
            for col, pid in zip(cols, row):
                with col:
                    # Silhouette
                    st.markdown(
                        f"<div style='text-align:center;'>"
                        f"<img src='{sprite_url(pid)}' width='80' "
                        f"style='filter:brightness(0);opacity:0.4;'/>"
                        f"<p style='font-size:0.7rem;color:#555;margin:0;'>???</p></div>",
                        unsafe_allow_html=True,
                    )

st.markdown("---")
if st.button("🗑️ Reset Pokédex", type="secondary"):
    reset_caught()
    st.rerun()
