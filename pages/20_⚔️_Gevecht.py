import streamlit as st
import random
from utils.styles import inject_custom_css
from utils.pokemon_data import POKEMON, POKEMON_IDS, get_stats, sprite_url, back_sprite_url
from utils.caught_pokemon import mark_caught

st.set_page_config(page_title="Pokémon Gevecht", page_icon="⚔️", layout="wide")
inject_custom_css()

# ── helpers ────────────────────────────────────────────────────────────────────

def calc_damage(attacker: dict, defender: dict, move: str) -> int:
    if move == "aanval":
        base = max(1, attacker["attack"] - defender["defense"] // 2)
        return random.randint(max(1, base - 5), base + 10)
    elif move == "speciaal":
        base = max(5, attacker["attack"] * 3 // 2 - defender["defense"] // 3)
        return random.randint(max(1, base - 5), base + 15)
    return 0  # verdediging doet geen schade


def new_battle(player_id: int | None = None, enemy_id: int | None = None):
    pid = player_id or random.choice(POKEMON_IDS)
    eid = enemy_id or random.choice([i for i in POKEMON_IDS if i != pid])
    ps  = get_stats(pid)
    es  = get_stats(eid)
    st.session_state.b_player_id    = pid
    st.session_state.b_enemy_id     = eid
    st.session_state.b_player_hp    = ps["hp"]
    st.session_state.b_player_maxhp = ps["hp"]
    st.session_state.b_enemy_hp     = es["hp"]
    st.session_state.b_enemy_maxhp  = es["hp"]
    st.session_state.b_player_stats = ps
    st.session_state.b_enemy_stats  = es
    st.session_state.b_log          = []
    st.session_state.b_over         = False
    st.session_state.b_defending    = False
    st.session_state.b_turn         = "player"  # "player" | "enemy" | "done"


def hp_bar(current: int, maximum: int, color: str = "#4caf50") -> str:
    pct = max(0, current / maximum * 100)
    bar_color = "#4caf50" if pct > 50 else "#ff9800" if pct > 20 else "#f44336"
    return (
        f"<div style='background:#333;border-radius:6px;height:14px;width:100%;'>"
        f"<div style='background:{bar_color};width:{pct:.0f}%;height:14px;border-radius:6px;"
        f"transition:width 0.3s;'></div></div>"
        f"<small>{current}/{maximum} HP</small>"
    )


# ── init ───────────────────────────────────────────────────────────────────────
if "b_player_id" not in st.session_state:
    new_battle()

# ── layout ────────────────────────────────────────────────────────────────────
st.markdown("## ⚔️ Pokémon Gevecht")

pid = st.session_state.b_player_id
eid = st.session_state.b_enemy_id
player_name = POKEMON[pid]
enemy_name  = POKEMON[eid]

# Sprite row
col_p, col_vs, col_e = st.columns([2, 1, 2])
with col_p:
    st.markdown(f"**Jouw Pokémon: {player_name}**")
    st.image(back_sprite_url(pid), width=160)
    st.markdown(hp_bar(st.session_state.b_player_hp, st.session_state.b_player_maxhp), unsafe_allow_html=True)
with col_vs:
    st.markdown("<div style='text-align:center;font-size:2.5rem;margin-top:60px;'>⚔️</div>", unsafe_allow_html=True)
with col_e:
    st.markdown(f"**Tegenstander: {enemy_name}**")
    st.image(sprite_url(eid), width=160)
    st.markdown(hp_bar(st.session_state.b_enemy_hp, st.session_state.b_enemy_maxhp), unsafe_allow_html=True)

st.markdown("---")

# ── battle logic ───────────────────────────────────────────────────────────────
if not st.session_state.b_over:
    if st.session_state.b_turn == "player":
        st.markdown("### Jouw beurt — kies een actie:")
        c1, c2, c3 = st.columns(3)

        move = None
        if c1.button("👊 Aanval", use_container_width=True):
            move = "aanval"
        if c2.button("✨ Speciaal", use_container_width=True):
            move = "speciaal"
        if c3.button("🛡️ Verdedigen", use_container_width=True):
            move = "verdediging"

        if move:
            st.session_state.b_defending = (move == "verdediging")
            if move != "verdediging":
                dmg = calc_damage(st.session_state.b_player_stats, st.session_state.b_enemy_stats, move)
                st.session_state.b_enemy_hp = max(0, st.session_state.b_enemy_hp - dmg)
                st.session_state.b_log.append(f"Jij gebruikte **{move}** → {enemy_name} verliest **{dmg} HP**")
            else:
                st.session_state.b_log.append("Jij koos voor **verdediging** — minder schade volgende beurt!")

            if st.session_state.b_enemy_hp <= 0:
                st.session_state.b_log.append(f"🏆 **{enemy_name} is verslagen! Jij wint!**")
                st.session_state.b_over = True
                st.session_state.b_turn = "done"
                mark_caught(eid)
            else:
                st.session_state.b_turn = "enemy"
            st.rerun()

    elif st.session_state.b_turn == "enemy":
        # Enemy AI: random move, slightly smarter when low HP
        enemy_hp_pct = st.session_state.b_enemy_hp / st.session_state.b_enemy_maxhp
        if enemy_hp_pct < 0.3:
            move = random.choice(["speciaal", "speciaal", "aanval"])
        else:
            move = random.choice(["aanval", "aanval", "speciaal", "verdediging"])

        defense_mult = 0.5 if st.session_state.b_defending else 1.0
        if move != "verdediging":
            raw_dmg = calc_damage(st.session_state.b_enemy_stats, st.session_state.b_player_stats, move)
            dmg = max(1, int(raw_dmg * defense_mult))
            st.session_state.b_player_hp = max(0, st.session_state.b_player_hp - dmg)
            shield_txt = " (jouw schild hielp!)" if st.session_state.b_defending and defense_mult < 1 else ""
            st.session_state.b_log.append(f"{enemy_name} gebruikte **{move}** → jij verliest **{dmg} HP**{shield_txt}")
        else:
            st.session_state.b_log.append(f"{enemy_name} koos voor **verdediging**.")

        st.session_state.b_defending = False

        if st.session_state.b_player_hp <= 0:
            st.session_state.b_log.append(f"💀 **Jouw {player_name} is verslagen! Je verliest.**")
            st.session_state.b_over = True
            st.session_state.b_turn = "done"
        else:
            st.session_state.b_turn = "player"
        st.rerun()

else:
    last = st.session_state.b_log[-1] if st.session_state.b_log else ""
    if "wint" in last:
        st.success(last)
        st.info(f"🎉 **{enemy_name}** is toegevoegd aan je Pokédex!")
    else:
        st.error(last)
    if st.button("🔄 Nieuw gevecht", type="primary", use_container_width=True):
        new_battle()
        st.rerun()

# ── battle log ─────────────────────────────────────────────────────────────────
if st.session_state.b_log:
    st.markdown("### 📋 Gevechtslog")
    for entry in reversed(st.session_state.b_log[:-1] if st.session_state.b_over else st.session_state.b_log):
        st.markdown(f"- {entry}")

# sidebar: pick your pokemon
with st.sidebar:
    st.markdown("### Kies jouw Pokémon")
    chosen = st.selectbox("Pokémon", options=POKEMON_IDS, format_func=lambda i: POKEMON[i])
    if st.button("Start met deze Pokémon"):
        new_battle(player_id=chosen)
        st.rerun()
