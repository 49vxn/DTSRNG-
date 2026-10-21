# 1stmvp
# throw words at things

import random

# TODO: move the data into a file later
CREATURES = {
    "claxon": {"name": "Claxon", "hp": 34, "atk": 9, "words": ["yell", "heckle"]},
    "mutter": {"name": "Mutter", "hp": 30, "atk": 8, "words": ["shush", "hum"]},
}

WORDS = {
    "yell": {"name": "Yell", "power": 9},
    "heckle": {"name": "Heckle", "power": 6},
    "shush": {"name": "Shush", "power": 7},
    "hum": {"name": "Hum", "power": 5},
}


def make_monster(key):
    thing = CREATURES[key]
    return {"name": thing["name"], "hp": thing["hp"], "atk": thing["atk"], "words": thing["words"]}


def hit(attacker, defender, word):
    damage = WORDS[word]["power"] + random.randint(0, 3)
    defender["hp"] = defender["hp"] - damage
    print(attacker["name"] + " uses " + WORDS[word]["name"] + " for " + str(damage) + ".")


def fight(player, enemy):
    me = player["party"][0]
    while True:
        print()
        print(me["name"] + " " + str(me["hp"]) + "   vs   " + enemy["name"] + " " + str(enemy["hp"]))
        print("1. speak   2. run")
        choice = input("> ")

        if choice == "2":
            print("You back away.")
            hit(enemy, me, random.choice(enemy["words"]))
            return

        if choice == "1":
            print("Which word?")
            for i in range(len(me["words"])):
                print(str(i + 1) + ". " + WORDS[me["words"][i]]["name"])
            pick = int(input("> "))
            hit(me, enemy, me["words"][pick - 1])
            if enemy["hp"] <= 0:
                print(enemy["name"] + " goes quiet.")
                return
            hit(enemy, me, random.choice(enemy["words"]))
            if me["hp"] <= 0:
                print(me["name"] + " goes quiet.")
                return
        else:
            print("1 or 2.")
            hit(enemy, me, random.choice(enemy["words"]))
            if me["hp"] <= 0:
                print(me["name"] + " goes quiet.")
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
            fight(player, make_monster("mutter"))
            return
        elif command == "quit":
            return
        else:
            print("Nothing answers.")


def main():
    print("RNG")
    print("roll of the dice")
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
        player = {"name": name, "party": [make_monster(starter)]}
        print(name + " takes the " + player["party"][0]["name"] + ".")
        room(player)
    elif choice == "2":
        print("The dice go back in the cup.")
    else:
        print("Pick 1 or 2.")


main()
