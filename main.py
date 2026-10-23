# rng - roll of the dice
# a text game about throwing words at things. run it with python main.py
#
# creatures are collections of words, and those words are the moves.
# the game is printed text and keyboard input only, so it needs nothing but the standard library.

import json
import os
import random

from rng.text import t

MAX_PARTY = 5
SAVE_PATH = "save.json"

# the starting creatures. each one carries two words and one phrase.
CREATURES = {
    "claxon": {"name": t("creature.claxon.name"), "type": "shout", "hp": 34, "atk": 9, "words": ["yell", "heckle"]},
    "mutter": {"name": t("creature.mutter.name"), "type": "hush", "hp": 30, "atk": 8, "words": ["shush", "hum"]},
    "lilt": {"name": t("creature.lilt.name"), "type": "song", "hp": 32, "atk": 8, "words": ["croon", "hum"]},
    "yawp": {"name": t("creature.yawp.name"), "type": "shout", "hp": 36, "atk": 10, "words": ["yell", "plain"]},
    "gossip": {"name": t("creature.gossip.name"), "type": "song", "hp": 34, "atk": 9, "words": ["croon", "heckle"]},
    "silence": {"name": t("creature.silence.name"), "type": "hush", "hp": 48, "atk": 9, "words": ["shush", "hum"]},
}

WORDS = {
    "yell": {"name": t("word.yell.name"), "power": 9, "type": "shout"},
    "heckle": {"name": t("word.heckle.name"), "power": 6, "type": "shout"},
    "shush": {"name": t("word.shush.name"), "power": 7, "type": "hush"},
    "hum": {"name": t("word.hum.name"), "power": 5, "type": "song"},
    "croon": {"name": t("word.croon.name"), "power": 8, "type": "song"},
    "plain": {"name": t("word.plain.name"), "power": 7, "type": "plain"},
}

# shout drowns song, song soothes hush, hush swallows shout
TYPE_BEATS = {
    "shout": "song",
    "song": "hush",
    "hush": "shout",
}

PHRASES = {
    "claxon": {"name": t("phrase.claxon.name"), "power": 18, "type": "shout"},
    "mutter": {"name": t("phrase.mutter.name"), "power": 14, "type": "hush"},
    "lilt": {"name": t("phrase.lilt.name"), "power": 12, "type": "song"},
    "yawp": {"name": t("phrase.yawp.name"), "power": 20, "type": "shout"},
    "gossip": {"name": t("phrase.gossip.name"), "power": 13, "type": "song"},
    "silence": {"name": t("phrase.silence.name"), "power": 22, "type": "hush"},
}

# the last creature is the only one that cannot be talked over
BOSS_KEYS = {"silence"}


class RestartGame(Exception):
    """raised when the player types restart, anywhere there is a prompt"""


def make_creature(key):
    base = CREATURES[key]
    return {
        "key": key,
        "name": base["name"],
        "type": base["type"],
        "hp": base["hp"],
        "max": base["hp"],
        "atk": base["atk"],
        "words": list(base["words"]),
        "phrase_used": False,
        "boss": key in BOSS_KEYS,
    }


def ask(prompt=None):
    # every prompt goes through here, so restart works even mid fight
    if prompt is None:
        prompt = t("system.prompt")
    answer = input(prompt).strip()
    if answer.lower() == "restart":
        raise RestartGame
    return answer


def strike(attacker, target, move):
    damage = move["power"] + attacker["atk"] // 2 + random.randint(0, 3)
    if TYPE_BEATS.get(move["type"]) == target["type"]:
        damage = damage * 2
        print(t("combat.strong", move_type=t("type." + move["type"]), target_type=t("type." + target["type"])))
    elif TYPE_BEATS.get(target["type"]) == move["type"]:
        damage = damage // 2
        print(t("combat.weak", move_type=t("type." + move["type"]), target_type=t("type." + target["type"])))
    if damage < 1:
        damage = 1
    target["hp"] = target["hp"] - damage
    if target["hp"] < 0:
        target["hp"] = 0
    print(t("combat.hit", attacker=attacker["name"], move=move["name"], damage=damage))
    # the Quiet survives anything clever. only plain speech finishes it.
    if target.get("boss") and target["hp"] <= 0 and move["type"] != "plain":
        target["hp"] = 1
        print(t("combat.boss_rule", foe=target["name"], word=WORDS["plain"]["name"]))


def choose_creature(party, prompt):
    while True:
        print(prompt)
        for i in range(len(party)):
            monster = party[i]
            print(f"{i + 1}. {monster['name']} {monster['hp']}/{monster['max']}")
        answer = ask()
        if answer.isdigit():
            index = int(answer) - 1
            if 0 <= index < len(party) and party[index]["hp"] > 0:
                return index
        print(t("combat.pick_number"))


def beaten(player, foe, can_recruit, is_final):
    print(t("combat.faint", name=foe["name"]))
    if is_final:
        ending(player)
        return
    if can_recruit and len(player["party"]) < MAX_PARTY:
        player["party"].append(foe)
        print(t("combat.recruit", name=foe["name"]))


def fight(player, foe, can_recruit=False, is_final=False):
    party = player["party"]
    active = 0
    if not player.get("taught"):
        print(t("combat.first_hint"))
        player["taught"] = True
    while True:
        if party[active]["hp"] <= 0:
            for i in range(len(party)):
                if party[i]["hp"] > 0:
                    active = i
                    break
            else:
                print(t("combat.no_words"))
                return False

        me = party[active]
        print()
        print(t("combat.status", name=me["name"], type=t("type." + me["type"]), hp=me["hp"], max=me["max"],
                foe=foe["name"], foe_type=t("type." + foe["type"]), foe_hp=foe["hp"], foe_max=foe["max"]))
        next_move = random.choice(foe["words"])
        next_word = WORDS[next_move]
        print(t("combat.intent", foe=foe["name"], word=next_word["name"],
                type=t("type." + next_word["type"])))
        phrase_state = t("combat.phrase_spent_label") if me["phrase_used"] else t("combat.phrase_ready")
        print(t("combat.menu", phrase_state=phrase_state))
        choice = ask()

        if choice == "5":
            return False
        if choice == "4":
            print(t("combat.run_away"))
            return False
        if choice == "3":
            active = choose_creature(party, t("combat.send_out"))
            me = party[active]
            strike(foe, me, WORDS[next_move])
            if me["hp"] <= 0:
                print(t("combat.faint", name=me["name"]))
            continue
        if choice == "2":
            if me["phrase_used"]:
                print(t("combat.phrase_spent"))
                continue
            me["phrase_used"] = True
            phrase = PHRASES[me["key"]]
            print(t("combat.phrase_speak", name=me["name"]))
            strike(me, foe, phrase)
            if foe["hp"] <= 0:
                beaten(player, foe, can_recruit, is_final)
                return is_final
            strike(foe, me, WORDS[next_move])
            if me["hp"] <= 0:
                print(t("combat.faint", name=me["name"]))
            continue
        if choice != "1":
            print(t("combat.invalid"))
            continue

        print(t("combat.which_word"))
        for i in range(len(me["words"])):
            word = WORDS[me["words"][i]]
            print(f"{i + 1}. {word['name']} ({t('type.' + word['type'])})")
        pick = ask()
        if not pick.isdigit() or int(pick) < 1 or int(pick) > len(me["words"]):
            print(t("combat.not_a_word"))
            continue

        strike(me, foe, WORDS[me["words"][int(pick) - 1]])
        if foe["hp"] <= 0:
            beaten(player, foe, can_recruit, is_final)
            return is_final

        strike(foe, me, WORDS[next_move])
        if me["hp"] <= 0:
            print(t("combat.faint", name=me["name"]))


AREAS = {
    "signpost": {
        "name": t("area.signpost.name"),
        "text": t("area.signpost.text"),
        "look": t("area.signpost.look"),
        "exits": {"north": "mile"},
        "foe": "mutter",
    },
    "mile": {
        "name": t("area.mile.name"),
        "text": t("area.mile.text"),
        "look": t("area.mile.look"),
        "exits": {"south": "signpost", "north": "archive"},
        "foe": "claxon",
        "rival": True,
        "puzzle": {
            "gate": "north",
            "prompt": t("puzzle.mile.prompt"),
            "answers": ["the gate opens if you ask nicely", "if you ask nicely the gate opens"],
            "hint": t("puzzle.mile.hint"),
        },
    },
    "archive": {
        "name": t("area.archive.name"),
        "text": t("area.archive.text"),
        "look": t("area.archive.look"),
        "exits": {"south": "mile", "north": "market"},
        "foe": "yawp",
        "recruit": True,
        "puzzle": {
            "gate": "north",
            "prompt": t("puzzle.archive.prompt"),
            "answers": ["me"],
            "hint": t("puzzle.archive.hint"),
        },
    },
    "market": {
        "name": t("area.market.name"),
        "text": t("area.market.text"),
        "look": t("area.market.look"),
        "exits": {"south": "archive", "north": "quiet"},
        "foe": "gossip",
        "recruit": True,
        "puzzle": {
            "gate": "north",
            "prompt": t("puzzle.market.prompt"),
            "answers": ["silence"],
            "hint": t("puzzle.market.hint"),
        },
    },
    "quiet": {
        "name": t("area.quiet.name"),
        "text": t("area.quiet.text"),
        "look": t("area.quiet.look"),
        "exits": {"north": "hollow", "south": "market"},
    },
    "hollow": {
        "name": t("area.hollow.name"),
        "text": t("area.hollow.text"),
        "look": t("area.hollow.look"),
        "exits": {"south": "quiet"},
        "foe": "silence",
        "ending": True,
    },
}


def has_plain(player):
    for monster in player["party"]:
        if "plain" in monster["words"]:
            return True
    return False


def rest_party(player):
    # the last house is quiet enough to get your breath back, so a hard fight can be retried
    rested = False
    for monster in player["party"]:
        if monster["hp"] < monster["max"] or monster["phrase_used"]:
            rested = True
        monster["hp"] = monster["max"]
        monster["phrase_used"] = False
    return rested


def take_chalk(player):
    # the chalk word is the only way to answer the Quiet, so the house hands it out
    print(t("house.chalk", word=WORDS["plain"]["name"]))
    for monster in player["party"]:
        if "plain" in monster["words"]:
            monster["words"].remove("plain")
        monster["words"].insert(0, "plain")
    print(t("house.chalk_pass"))


def ending(player):
    print()
    print(t("ending.part1", foe=CREATURES["silence"]["name"]))
    print(t("ending.part2"))
    print()
    print(t("ending.walk", name=player["name"]))
    print(t("ending.world1"))
    print(t("ending.world2"))
    print()
    print(t("ending.thesis"))
    print()
    print(t("ending.the_end"))
    # a finished story should not be continued from the title screen
    try:
        os.remove(SAVE_PATH)
    except FileNotFoundError:
        pass


def show_party(player):
    print(t("party.title", name=player["name"]))
    for monster in player["party"]:
        print(t("party.line", name=monster["name"], type=t(f"type.{monster['type']}"),
                hp=monster["hp"], max=monster["max"]))
        print(t("party.phrase", phrase=PHRASES[monster["key"]]["name"]))


def save_game(player, spot):
    data = {
        "name": player["name"],
        "party": player["party"],
        "solved": player["solved"],
        "tries": player["tries"],
        "rival": player["rival"],
        "chalk": player.get("chalk", False),
        "taught": player.get("taught", False),
        "spot": spot,
    }
    with open(SAVE_PATH, "w") as handle:
        json.dump(data, handle)


def load_game():
    try:
        with open(SAVE_PATH) as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def normalise(text):
    # puzzle answers ignore case, punctuation and extra spaces
    text = text.lower().strip()
    for mark in ".,!?;:'\"-":
        text = text.replace(mark, "")
    return " ".join(text.split())


def explore(player, spot):
    save_game(player, spot)
    while True:
        here = AREAS[spot]
        print()
        print(here["name"])
        if spot == "quiet":
            if not player.get("chalk"):
                take_chalk(player)
                player["chalk"] = True
            if rest_party(player):
                print(t("house.rest"))
        print(here["text"])
        print(t("system.commands", exits=", ".join(here["exits"])))

        command = ask().lower()
        if command.startswith("go "):
            command = command[3:]

        if command == "look":
            print(here["look"])
        elif command == "help":
            instructions()
        elif command == "party":
            show_party(player)
        elif command in here["exits"]:
            gate = here.get("puzzle", {}).get("gate")
            if command == gate and here["name"] not in player["solved"]:
                print(here["puzzle"]["prompt"])
                answer = ask()
                tries = player["tries"].get(here["name"], 0) + 1
                player["tries"][here["name"]] = tries
                if normalise(answer) in [normalise(one) for one in here["puzzle"]["answers"]]:
                    print(t("puzzle.open"))
                    player["solved"].append(here["name"])
                    spot = here["exits"][command]
                    save_game(player, spot)
                else:
                    print(t("puzzle.wrong"))
                    if tries >= 3:
                        print(here["puzzle"]["hint"])
            else:
                spot = here["exits"][command]
                save_game(player, spot)
        elif command == "fight":
            foe = player["rival"] if here.get("rival") else here["foe"]
            finished = fight(player, make_creature(foe), here.get("recruit", False), here.get("ending", False))
            if finished:
                return
        elif command == "quit":
            return
        else:
            print(t("system.unknown"))


def instructions():
    print()
    print(t("help.intro"))
    print(t("help.types"))
    print(t("help.phrases"))
    print(t("help.commands"))
    print(t("help.restart"))


def title():
    while True:
        print(t("title.name"))
        print(t("title.subtitle"))
        print()
        print("1. " + t("menu.new_game"))
        print("2. " + t("menu.continue"))
        print("3. " + t("menu.how_to_play"))
        print("4. " + t("menu.quit"))
        print("(" + t("menu.hint") + ")")
        choice = ask()

        if choice == "1":
            name = ""
            while not name:
                name = input(t("start.name_prompt")).strip()
                if not name:
                    print(t("start.name_needed"))
            print(t("start.pick_two"))
            starters = {}
            for key in ("claxon", "mutter", "lilt"):
                starters[key] = CREATURES[key]["name"]
                starters[key + "_type"] = t("type." + CREATURES[key]["type"])
            print(t("start.starters", **starters))
            picks = {"1": "claxon", "2": "mutter", "3": "lilt"}
            first = None
            while first is None:
                choice = ask()
                first = picks.get(choice)
                if first is None:
                    print(t("start.pick_invalid"))
            print(t("start.and_one"))
            second = None
            while second is None:
                choice = ask()
                second = picks.get(choice)
                if second is None:
                    print(t("start.pick_invalid"))
            if second == first:
                second = "lilt" if first != "lilt" else "claxon"
            party = [make_creature(first), make_creature(second)]
            rival = [key for key in picks.values() if key not in (first, second)][0]
            player = {"name": name, "party": party, "solved": [], "tries": {}, "rival": rival, "chalk": False}
            print(t("start.chosen", name=name, first=party[0]["name"], second=party[1]["name"]))
            save_game(player, "signpost")
            explore(player, "signpost")
        elif choice == "2":
            data = load_game()
            if data is None:
                print(t("save.none"))
                continue
            player = {
                "name": data["name"],
                "party": data["party"],
                "solved": data["solved"],
                "tries": data.get("tries", {}),
                "rival": data["rival"],
                "chalk": data.get("chalk", False),
                "taught": data.get("taught", False),
            }
            for monster in player["party"]:
                monster["hp"] = monster["max"]
                monster["phrase_used"] = False
            print(t("save.continue", name=player["name"]))
            explore(player, data["spot"])
        elif choice == "3":
            instructions()
        elif choice == "4":
            print(t("system.quit"))
            return
        else:
            print(t("menu.invalid"))


def main():
    while True:
        try:
            title()
        except RestartGame:
            print("\n" + t("system.restart"))
            continue
        return


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        # closing the window or pressing ctrl-c should not dump a traceback
        print("\n" + t("system.quit"))
