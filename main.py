# rng - roll of the dice
# a text game about throwing words at things. run it with python main.py

import json
import random

MAX_PARTY = 5
SAVE_PATH = "save.json"

CREATURES = {
    "claxon": {"name": "Claxon", "type": "shout", "hp": 34, "atk": 9, "words": ["yell", "heckle"]},
    "mutter": {"name": "Mutter", "type": "hush", "hp": 30, "atk": 8, "words": ["shush", "hum"]},
    "lilt": {"name": "Lilt", "type": "song", "hp": 32, "atk": 8, "words": ["croon", "hum"]},
    "yawp": {"name": "Yawp", "type": "shout", "hp": 36, "atk": 10, "words": ["yell", "plain"]},
    "gossip": {"name": "Gossip", "type": "song", "hp": 34, "atk": 9, "words": ["croon", "heckle"]},
}

WORDS = {
    "yell": {"name": "Yell", "power": 9, "type": "shout"},
    "heckle": {"name": "Heckle", "power": 6, "type": "shout"},
    "shush": {"name": "Shush", "power": 7, "type": "hush"},
    "hum": {"name": "Hum", "power": 5, "type": "song"},
    "croon": {"name": "Croon", "power": 8, "type": "song"},
    "plain": {"name": "Plain Talk", "power": 7, "type": "plain"},
}

# shout drowns song, song soothes hush, hush swallows shout
TYPE_BEATS = {
    "shout": "song",
    "song": "hush",
    "hush": "shout",
}

PHRASES = {
    "claxon": {"name": "Sound the Alarm", "power": 18, "type": "shout"},
    "mutter": {"name": "Dead Air", "power": 14, "type": "hush"},
    "lilt": {"name": "Lullaby", "power": 12, "type": "song"},
    "yawp": {"name": "Foghorn", "power": 20, "type": "shout"},
    "gossip": {"name": "Rumour", "power": 13, "type": "song"},
}


def make_creature(key):
    base = CREATURES[key]
    return {
        "key": key,
        "name": base["name"],
        "type": base["type"],
        "hp": base["hp"],
        "max": base["hp"],
        "atk": base["atk"],
        "words": base["words"],
        "phrase_used": False,
    }


def strike(attacker, target, move):
    damage = move["power"] + attacker["atk"] // 2 + random.randint(0, 3)
    if TYPE_BEATS.get(move["type"]) == target["type"]:
        damage = damage * 2
        print("It lands hard.")
    elif TYPE_BEATS.get(target["type"]) == move["type"]:
        damage = damage // 2
        print("It barely lands.")
    if damage < 1:
        damage = 1
    target["hp"] = target["hp"] - damage
    if target["hp"] < 0:
        target["hp"] = 0
    print(f"{attacker['name']} uses {move['name']} for {damage}.")


def choose_creature(party, prompt):
    while True:
        print(prompt)
        for i in range(len(party)):
            monster = party[i]
            print(f"{i + 1}. {monster['name']} {monster['hp']}/{monster['max']}")
        answer = input("> ")
        if answer.isdigit():
            index = int(answer) - 1
            if 0 <= index < len(party) and party[index]["hp"] > 0:
                return index
        print("Pick a number from the list.")


def fight(player, foe, can_recruit=False):
    party = player["party"]
    active = 0
    while True:
        if party[active]["hp"] <= 0:
            for i in range(len(party)):
                if party[i]["hp"] > 0:
                    active = i
                    break
            else:
                print("You have no words left.")
                return

        me = party[active]
        print()
        print(f"{me['name']} {me['hp']}/{me['max']}   vs   {foe['name']} {foe['hp']}/{foe['max']}")
        next_move = random.choice(foe["words"])
        print(f"The {foe['name']} is winding up: {WORDS[next_move]['name']}.")
        print("1. speak   2. phrase   3. switch   4. run   5. quit")
        choice = input("> ")

        if choice == "5":
            return
        if choice == "4":
            print("You get out of the grass.")
            return
        if choice == "3":
            active = choose_creature(party, "Send out who?")
            me = party[active]
            strike(foe, me, WORDS[next_move])
            if me["hp"] <= 0:
                print(f"{me['name']} goes quiet.")
            continue
        if choice == "2":
            if me["phrase_used"]:
                print("The phrase is spent.")
                continue
            me["phrase_used"] = True
            phrase = PHRASES[me["key"]]
            print(f"{me['name']} speaks its phrase.")
            strike(me, foe, phrase)
            if foe["hp"] <= 0:
                print(f"{foe['name']} goes quiet.")
                if can_recruit and len(party) < MAX_PARTY:
                    party.append(foe)
                    print(f"{foe['name']} joins you.")
                return
            strike(foe, me, WORDS[next_move])
            if me["hp"] <= 0:
                print(f"{me['name']} goes quiet.")
            continue
        if choice != "1":
            print("1, 2, 3, 4 or 5.")
            continue

        print("Which word?")
        for i in range(len(me["words"])):
            print(f"{i + 1}. {WORDS[me['words'][i]]['name']}")
        pick = input("> ")
        if not pick.isdigit() or int(pick) < 1 or int(pick) > len(me["words"]):
            print("That is not a word.")
            continue

        strike(me, foe, WORDS[me["words"][int(pick) - 1]])
        if foe["hp"] <= 0:
            print(f"{foe['name']} goes quiet.")
            if can_recruit and len(party) < MAX_PARTY:
                party.append(foe)
                print(f"{foe['name']} joins you.")
            return

        strike(foe, me, WORDS[next_move])
        if me["hp"] <= 0:
            print(f"{me['name']} goes quiet.")


AREAS = {
    "signpost": {
        "name": "The Signpost Field",
        "text": "A field of blank signpsots. The grass is wet. One road goes north.",
        "look": "The signposts have no names on them. The north road is shut by a gate.",
        "exits": {"north": "mile"},
        "foe": "mutter",
    },
    "mile": {
        "name": "The Crooked Mile",
        "text": "The road bends left and then left again. Someone is waiting on the verge with a creature you almost recognise.",
        "look": "The mile goes on. The rival's creature is watching you, not the road.",
        "exits": {"south": "signpost", "north": "archive"},
        "foe": "claxon",
        "rival": True,
        "puzzle": {
            "gate": "north",
            "prompt": "A sentence is nailed across the gate. Put it in order: opens / the / gate / if / ask / you / nicely",
            "answers": ["the gate opens if you ask nicely", "if you ask nicely the gate opens"],
            "hint": "Start with the gate.",
        },
    },
    "archive": {
        "name": "The Drowned Archive",
        "text": "A library under a foot of water. The shelves go down further than the room. A drain is set in the floor, and a sentence is carved around it.",
        "look": "The water is warm. Something with a foghorn throat is asleep on the desk.",
        "exits": {"south": "mile", "north": "market"},
        "foe": "yawp",
        "recruit": True,
        "puzzle": {
            "gate": "north",
            "prompt": "The drain says: Between you and ___, the archive is drowning.",
            "answers": ["me"],
            "hint": "It is not I.",
        },
    },
    "market": {
        "name": "The Market of Small Lies",
        "text": "A row of stalls selling words by the letter. A small many-tongued thing is sitting on the counter of the closed stall.",
        "look": "The signs are spelled wrong on purpose. The thing on the counter is already telling someone about you.",
        "exits": {"south": "archive"},
        "foe": "gossip",
    },
}


def show_party(player):
    print(f"{player['name']}'s words:")
    for monster in player["party"]:
        print(f"  {monster['name']} ({monster['type']}) {monster['hp']}/{monster['max']}")
        print(f"    phrase: {PHRASES[monster['key']]['name']}")


def save_game(player, spot):
    data = {
        "name": player["name"],
        "party": player["party"],
        "solved": player["solved"],
        "rival": player["rival"],
        "spot": spot,
    }
    with open(SAVE_PATH, "w") as handle:
        json.dump(data, handle)


def load_game():
    try:
        with open(SAVE_PATH) as handle:
            return json.load(handle)
    except FileNotFoundError:
        return None


def normalise(text):
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
        print(here["text"])
        print("Commands: look, " + ", ".join(here["exits"]) + ", fight, quit")

        command = input("> ").lower()
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
                answer = input("> ")
                if normalise(answer) in [normalise(one) for one in here["puzzle"]["answers"]]:
                    print("The gate opens.")
                    player["solved"].append(here["name"])
                    spot = here["exits"][command]
                    save_game(player, spot)
                else:
                    print("The gate does not move.")
            else:
                spot = here["exits"][command]
                save_game(player, spot)
        elif command == "fight":
            foe = player["rival"] if here.get("rival") else here["foe"]
            fight(player, make_creature(foe), here.get("recruit", False))
        elif command == "quit":
            return
        else:
            print("Nothing answers.")


def instructions():
    print()
    print("You are a roller. Words fight for you, in turns.")
    print("Shout beats song, song beats hush, hush beats shout.")
    print("Every creature has two words and one phrase. A phrase works once per fight.")
    print("Commands: look, go north, go south, party, help, fight, quit")


def main():
    while True:
        print("RNG")
        print("roll of the dice")
        print()
        print("1. new game")
        print("2. continue")
        print("3. how to play")
        print("4. quit")
        choice = input("> ")

        if choice == "1":
            name = input("Name: ")
            print("Three words are waiting on the table. Pick two.")
            print("1. Claxon   2. Mutter   3. Lilt")
            picks = {"1": "claxon", "2": "mutter", "3": "lilt"}
            first = picks.get(input("> "), "claxon")
            print("And one more.")
            second = picks.get(input("> "), "mutter")
            if second == first:
                second = "lilt" if first != "lilt" else "claxon"
            party = [make_creature(first), make_creature(second)]
            rival = [key for key in picks.values() if key not in (first, second)][0]
            player = {"name": name, "party": party, "solved": [], "rival": rival}
            print(f"{name} takes the {party[0]['name']} and the {party[1]['name']}.")
            save_game(player, "signpost")
            explore(player, "signpost")
        elif choice == "2":
            data = load_game()
            if data is None:
                print("There is no page to turn back to.")
                continue
            player = {
                "name": data["name"],
                "party": data["party"],
                "solved": data["solved"],
                "rival": data["rival"],
            }
            for monster in player["party"]:
                monster["hp"] = monster["max"]
                monster["phrase_used"] = False
            print(f"{player['name']} picks up where they left off.")
            explore(player, data["spot"])
        elif choice == "3":
            instructions()
        elif choice == "4":
            print("The dice go back in the cup.")
            return
        else:
            print("Pick 1, 2, 3 or 4.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        # closing the window or pressing ctrl-c should not dump a traceback
        print("\nThe dice go back in the cup.")
