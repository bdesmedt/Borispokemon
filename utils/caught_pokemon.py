"""
Persistent caught-Pokémon storage.
Data is saved as JSON: { "<pokemon_id>": <catch_count>, ... }
"""
import json
import os

_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "caught.json")


def _load() -> dict[int, int]:
    try:
        with open(_DATA_FILE, "r") as f:
            raw = json.load(f)
        return {int(k): v for k, v in raw.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict[int, int]) -> None:
    os.makedirs(os.path.dirname(_DATA_FILE), exist_ok=True)
    with open(_DATA_FILE, "w") as f:
        json.dump({str(k): v for k, v in data.items()}, f, indent=2)


def load_caught() -> dict[int, int]:
    """Return {pokemon_id: times_caught}."""
    return _load()


def mark_caught(pokemon_id: int) -> None:
    """Increment the catch count for a Pokémon."""
    data = _load()
    data[pokemon_id] = data.get(pokemon_id, 0) + 1
    _save(data)


def reset_caught() -> None:
    """Clear all caught data."""
    _save({})
