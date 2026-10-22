import json
from pathlib import Path

TEXT_PATH = Path(__file__).with_name("text.json")


def load_text(path=TEXT_PATH):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    values = {}
    for group in data["groups"]:
        for entry in group["entries"]:
            values[entry["key"]] = entry["value"]
    return values


TEXTS = load_text()


def t(key, **values):
    # every printed line comes from text.json, so the writing can change without touching the logic
    if key not in TEXTS:
        raise KeyError(f"no text for {key}")
    return TEXTS[key].format(**values)
