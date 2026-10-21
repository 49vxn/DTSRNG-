# rng - roll of the dice
# a text game about throwing words at things. run it with python main.py

import random

CREATURES = {
    "claxon": {"name": "Clarion", "hp": 34, "atk": 9, "words": ["yell", "heckle"]},
    "mutter": {"name": "Murmur", "hp": 30, "atk": 8, "words": ["shush", "hum"]},
}

WORDS = {
    "yell": {"name": "Outcry", "power": 9},
    "heckle": {"name": "Jeer", "power": 6},
    "shush": {"name": "Shush", "power": 7},
    "hum": {"name": "Drone", "power": 5},
}


def make_creature(key):
    base = CREATURES[key]
    return {
        "name": base["name"],
        "hp": base["hp"],
        "max": base["hp"],
        "atk": base["atk"],
        "words": base["words"],
    }


def strike(attacker, target, word):
    damage = WORDS[word]["power"] + attacker["atk"] // 2 + random.randint(0, 3)
    target["hp"] = target["hp"] - damage
    if target["hp"] < 0:
        target["hp"] = 0
    print(f"{attacker['name']} uses {WORDS[word]['name']} for {damage}.")


def fight(player, foe):
    me = player["party"][0]
    while True:
        print()
        print(f"{me['name']} {me['hp']}/{me['max']}   vs   {foe['name']} {foe['hp']}/{foe['max']}")
        print("1. speak   2. run   3. quit")
        choice = input("> ")

        if choice == "3":
            return

        if choice == "2":
            print("You back away.")
            strike(foe, me, random.choice(foe["words"]))
            return

        if choice != "1":
            print("1, 2 or 3.")
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
            return

        strike(foe, me, random.choice(foe["words"]))
        if me["hp"] <= 0:
            print(f"{me['name']} goes quiet.")
            return


def room(player):
    print()
    print("The Signpost Field")
    print("A field of blank signpsots. The grass is wet. One road goes north.")
    print("Something small is worrying at the grass. It looks up.")
    print("Commands: look, north, fight, quit")

    while True:
        command = input("> ").lower()
        if command == "look":
            print("The signposts have no names on them. The north road is shut by a gate.")
        elif command == "north":
            print("The gate is shut.")
        elif command == "fight":
            fight(player, make_creature("mutter"))
            return
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
            print("1. Claxon   2. Mutter")
            pick = input("> ")
            if pick == "2":
                starter = "mutter"
            else:
                starter = "claxon"
            player = {"name": name, "party": [make_creature(starter)]}
            print(f"{name} takes the {player['party'][0]['name']}.")
            room(player)
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