import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

DEFAULT_MEMORY = {
    "profile": {},      # stable facts about you (name, birthday, city, etc.)
    "preferences": {},  # likes/dislikes (food, music, games, etc.)
    "facts": [],        # list of individual memories with metadata
}


def _ensure_memory_file():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_MEMORY, f, indent=4, ensure_ascii=False)


def load_memory():
    _ensure_memory_file()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # migrate old simple structure if needed
    if "profile" not in data or "preferences" not in data or "facts" not in data:
        new_data = DEFAULT_MEMORY.copy()
        # old version might have "user_profile"
        if "user_profile" in data and isinstance(data["user_profile"], dict):
            for k, v in data["user_profile"].items():
                new_data["profile"][k] = v
                new_data["facts"].append(_make_fact(k, v, "profile"))
        data = new_data
        save_memory(data)

    return data


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _guess_category(key: str) -> str:
    k = key.lower()
    profile_keywords = ["name", "birthday", "birth", "age", "school", "college", "city", "country", "job"]
    pref_keywords = ["favorite", "favourite", "like", "love", "hate", "music", "song", "game", "food", "color", "colour"]

    if any(word in k for word in profile_keywords):
        return "profile"
    if any(word in k for word in pref_keywords):
        return "preferences"
    return "general"


def _make_fact(key: str, value: str, category: str):
    now = _now_iso()
    return {
        "key": key,
        "value": value,
        "category": category,
        "created_at": now,
        "last_used_at": now,
    }


def remember_fact_advanced(key: str, value: str, category: str | None = None):
    """
    Store or update a fact with category & timestamps.
    Also syncs into profile/preferences dicts.
    """
    key = key.strip()
    value = value.strip()
    if not key or not value:
        return

    data = load_memory()

    if category is None:
        category = _guess_category(key)

    # update quick views
    if category == "profile":
        data["profile"][key] = value
    elif category == "preferences":
        data["preferences"][key] = value

    # update or append in facts list
    found = False
    for fact in data["facts"]:
        if fact["key"].lower() == key.lower():
            fact["value"] = value
            fact["category"] = category
            fact["last_used_at"] = _now_iso()
            found = True
            break

    if not found:
        data["facts"].append(_make_fact(key, value, category))

    save_memory(data)


def forget_fact(key: str) -> bool:
    data = load_memory()
    key_lower = key.lower()

    removed = False

    # remove from profile
    for k in list(data["profile"].keys()):
        if k.lower() == key_lower:
            del data["profile"][k]
            removed = True

    # remove from preferences
    for k in list(data["preferences"].keys()):
        if k.lower() == key_lower:
            del data["preferences"][k]
            removed = True

    # remove from facts list
    new_facts = []
    for fact in data["facts"]:
        if fact["key"].lower() != key_lower:
            new_facts.append(fact)
        else:
            removed = True
    data["facts"] = new_facts

    if removed:
        save_memory(data)

    return removed


def get_fact(key: str) -> str | None:
    data = load_memory()
    key_lower = key.lower()

    # search profile, preferences, then facts
    for k, v in data["profile"].items():
        if k.lower() == key_lower:
            return v

    for k, v in data["preferences"].items():
        if k.lower() == key_lower:
            return v

    for fact in data["facts"]:
        if fact["key"].lower() == key_lower:
            return fact["value"]

    return None


def list_all_memory() -> dict:
    """
    Return a simple structured view: profile + preferences + facts.
    """
    return load_memory()


def get_all_facts():
    """
    Return a flat list of all fact entries (for AI summarization).
    """
    data = load_memory()
    return data.get("facts", [])


def search_memory(query: str):
    """
    Simple search across keys & values (case-insensitive).
    Returns a list of matching fact dicts.
    """
    query = query.lower().strip()
    if not query:
        return []

    data = load_memory()
    results = []

    # search profile
    for k, v in data["profile"].items():
        if query in k.lower() or query in v.lower():
            results.append(_make_fact(k, v, "profile"))

    # search preferences
    for k, v in data["preferences"].items():
        if query in k.lower() or query in v.lower():
            results.append(_make_fact(k, v, "preferences"))

    # search other facts
    for fact in data["facts"]:
        if query in fact["key"].lower() or query in fact["value"].lower():
            results.append(fact)

    return results
