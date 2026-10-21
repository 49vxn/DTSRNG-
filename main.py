# rng - roll of the dice
# a text game about throwing words at things. run it with python main.py

import random

CREATURES = {
    "claxon": {"name": "Clarion", "type": "shout", "hp": 34, "atk": 9, "words": ["yell", "heckle"]},
    "mutter": {"name": "Murmur", "type": "hush", "hp": 30, "atk": 8, "words": ["shush", "hum"]},
    "lilt": {"name": "Cadence", "type": "song", "hp": 32, "atk": 8, "words": ["croon", "hum"]},
}

WORDS = {
    "yell": {"name": "Outcry", "power": 9, "type": "shout"},
    "heckle": {"name": "Jeer", "power": 6, "type": "shout"},
    "shush": {"name": "Shush", "power": 7, "type": "hush"},
    "hum": {"name": "Drone", "power": 5, "type": "song"},
    "croon": {"name": "Refrain", "power": 8, "type": "song"},
}

# shout drowns song, song soothes hush, hush swallows shout
TYPE_BEATS = {
    "shout": "song",
    "song": "hush",
    "hush": "shout",
}


def make_creature(key):
    base = CREATURES[key]
    return {
        "name": base["name"],
        "type": base["type"],
        "hp": base["hp"],
        "max": base["hp"],
        "atk": base["atk"],
        "words": base["words"],
    }


def strike(attacker, target, word):
    move = WORDS[word]
    damage = move["power"] + attacker["atk"] // 2 + random.randint(0, 3)
    if TYPE_BEATS.get(move["type"]) == target["type"]:
        damage = damage * 2
        print("The word hits deep.")
    elif TYPE_BEATS.get(target["type"]) == move["type"]:
        damage = damage // 2
        print("The word glances off.")
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


def fight(player, foe):
    party = player["party"]
    active = 0
    while True:
        if party[active]["hp"] <= 0:
            for i in range(len(party)):
                if party[i]["hp"] > 0:
                    active = i
                    break
            else:
                print("Your throat is empty.")
                return

        me = party[active]
        print()
        print(f"{me['name']} {me['hp']}/{me['max']}   vs   {foe['name']} {foe['hp']}/{foe['max']}")
        print("1. speak   2. switch   3. run   4. quit")
        choice = input("> ")

        if choice == "4":
            return
        if choice == "3":
            print("You get out of the grass.")
            return
        if choice == "2":
            active = choose_creature(party, "Send out who?")
            me = party[active]
            strike(foe, me, random.choice(foe["words"]))
            if me["hp"] <= 0:
                print(f"{me['name']} goes quiet.")
            continue
        if choice != "1":
            print("1, 2, 3 or 4.")
            continue

        print("Which word?")
        for i in range(len(me["words"])):
            print(f"{i + 1}. {WORDS[me['words'][i]]['name']}")
        pick = input("> ")
        if not pick.isdigit() or int(pick) < 1 or int(pick) > len(me["words"]):
            print("That is not a word.")
            continue

        strike(me, foe, me["words"][int(pick) - 1])
        if foe["hp"] <= 0:
            print(f"{foe['name']} goes quiet.")
            if len(party) < 3:
                party.append(foe)
                print(f"{foe['name']} joins you.")
            return

        strike(foe, me, random.choice(foe["words"]))
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
        "text": "The road bends left and then left again. A brass-coloured thing is sitting on the verge.",
        "look": "The mile goes on. The grass is flattened where something has been sitting.",
        "exits": {"south": "signpost"},
        "foe": "claxon",
    },
}


def explore(player, spot):
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
        elif command in here["exits"]:
            spot = here["exits"][command]
        elif command == "fight":
            fight(player, make_creature(here["foe"]))
        elif command == "quit":
            return
        else:
            print("Nothing answers.")


def main():
    while True:
        print("RNG")
        print("roll of the dice")
        print()
        print("1. new game")
        print("2. quit")
        choice = input("> ")

        if choice == "1":
            name = input("Name: ")
            print("Pick a creature.")
            print("1. Clarion   2. Murmur   3. Cadence")
            pick = input("> ")
            if pick == "2":
                starter = "mutter"
            elif pick == "3":
                starter = "lilt"
            else:
                starter = "claxon"
            player = {"name": name, "party": [make_creature(starter)]}
            print(f"{name} takes the {player['party'][0]['name']}.")
            explore(player, "signpost")
        elif choice == "2":
            print("The dice go back in the cup.")
            return
        else:
            print("Pick 1 or 2.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        # closing the window or pressing ctrl-c should not dump a traceback
        print("\nThe dice go back in the cup.")