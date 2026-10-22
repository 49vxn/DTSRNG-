# tests for rng. run with: python -m unittest -v test_game

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import main
from rng.text import t


def player_at(spot_key, party=None):
    return {
        "name": "Tester",
        "party": party or [main.make_creature("claxon"), main.make_creature("mutter")],
        "solved": [],
        "tries": {},
        "rival": "mutter" if spot_key != "mile" else "lilt",
    }


class GameTestCase(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        main.SAVE_PATH = os.path.join(self.folder.name, "save.json")
        self.output = io.StringIO()

    def tearDown(self):
        self.folder.cleanup()

    def run_input(self, lines, call):
        with mock.patch("builtins.input", side_effect=lines), redirect_stdout(self.output):
            result = call()
        return result

    def text(self):
        return self.output.getvalue()


class DamageTests(GameTestCase):
    def test_advantage_doubles_damage(self):
        attacker = main.make_creature("claxon")          # atk 9, shout
        target = main.make_creature("lilt")              # song
        with mock.patch("main.random.randint", return_value=0):
            self.run_input([], lambda: main.strike(attacker, target, main.WORDS["yell"]))
        # 9 power + 4 from atk, doubled because shout beats song
        self.assertEqual(target["hp"], 32 - 26)
        self.assertIn(t("combat.strong", move_type=t("type.shout"), target_type=t("type.song")), self.text())

    def test_disadvantage_halves_damage(self):
        attacker = main.make_creature("claxon")          # shout
        target = main.make_creature("mutter")            # hush, beats shout
        with mock.patch("main.random.randint", return_value=0):
            self.run_input([], lambda: main.strike(attacker, target, main.WORDS["yell"]))
        self.assertEqual(target["hp"], 30 - 6)
        self.assertIn(t("combat.weak", move_type=t("type.shout"), target_type=t("type.hush")), self.text())

    def test_hp_never_goes_below_zero(self):
        attacker = main.make_creature("claxon")
        target = main.make_creature("lilt")
        target["hp"] = 2
        with mock.patch("main.random.randint", return_value=0):
            self.run_input([], lambda: main.strike(attacker, target, main.WORDS["yell"]))
        self.assertEqual(target["hp"], 0)

    def test_damage_is_never_zero(self):
        attacker = main.make_creature("mutter")          # atk 8, hush
        target = main.make_creature("claxon")            # shout, beats hush
        with mock.patch("main.random.randint", return_value=0):
            self.run_input([], lambda: main.strike(attacker, target, main.WORDS["hum"]))
        self.assertLess(target["hp"], target["max"])


class BossTests(GameTestCase):
    def test_clever_word_cannot_finish_the_quiet(self):
        attacker = main.make_creature("claxon")
        boss = main.make_creature("silence")
        boss["hp"] = 5
        with mock.patch("main.random.randint", return_value=0):
            self.run_input([], lambda: main.strike(attacker, boss, main.WORDS["yell"]))
        self.assertEqual(boss["hp"], 1)
        self.assertIn(t("combat.boss_rule", foe=boss["name"], word=main.WORDS["plain"]["name"]), self.text())

    def test_plain_speech_can_finish_the_quiet(self):
        attacker = main.make_creature("gossip")
        boss = main.make_creature("silence")
        boss["hp"] = 5
        with mock.patch("main.random.randint", return_value=0):
            self.run_input([], lambda: main.strike(attacker, boss, main.WORDS["plain"]))
        self.assertEqual(boss["hp"], 0)

    def test_ending_prints_and_clears_the_save(self):
        with open(main.SAVE_PATH, "w") as handle:
            handle.write("{}")
        boss = main.make_creature("silence")
        self.run_input([], lambda: main.beaten(player_at("quiet"), boss, False, True))
        self.assertIn(t("ending.the_end"), self.text())
        self.assertFalse(os.path.exists(main.SAVE_PATH))

    def test_normal_win_does_not_print_the_ending(self):
        foe = main.make_creature("mutter")
        player = player_at("signpost")
        self.run_input([], lambda: main.beaten(player, foe, True, False))
        self.assertNotIn(t("ending.the_end"), self.text())
        self.assertIn(t("combat.recruit", name=foe["name"]), self.text())


class ChalkTests(GameTestCase):
    def test_chalk_is_given_once_to_the_whole_party(self):
        player = player_at("quiet")
        self.run_input([], lambda: [main.take_chalk(player), main.take_chalk(player)])
        words = player["party"][0]["words"]
        self.assertEqual(words.count("plain"), 1)
        self.assertIn("plain", player["party"][1]["words"])

    def test_walking_into_the_quiet_house_hands_over_the_word(self):
        player = player_at("quiet")
        self.run_input(["quit"], lambda: main.explore(player, "quiet"))
        self.assertIn(t("word.plain.name"), self.text())
        self.assertTrue(main.has_plain(player))

    def test_chalk_is_handed_out_even_when_one_creature_already_says_plain(self):
        party = [main.make_creature("yawp"), main.make_creature("claxon")]
        player = player_at("quiet", party)
        self.run_input(["quit"], lambda: main.explore(player, "quiet"))
        for monster in player["party"]:
            self.assertEqual(monster["words"][0], "plain")
        self.assertTrue(player["chalk"])

    def test_the_house_only_hands_over_the_chalk_once(self):
        player = player_at("quiet")
        self.run_input(["quit"], lambda: main.explore(player, "quiet"))
        player["party"][0]["words"].remove("plain")
        self.run_input(["quit"], lambda: main.explore(player, "quiet"))
        self.assertNotIn("plain", player["party"][0]["words"])


class PuzzleTests(GameTestCase):
    def test_wrong_answer_holds_the_gate(self):
        player = player_at("mile")
        self.run_input(["north", "no", "quit"], lambda: main.explore(player, "mile"))
        self.assertIn(t("puzzle.wrong"), self.text())
        self.assertEqual(player["solved"], [])

    def test_third_wrong_answer_shows_the_hint(self):
        player = player_at("mile")
        self.run_input(["north", "no", "north", "no", "north", "no", "quit"],
                       lambda: main.explore(player, "mile"))
        self.assertIn(t("puzzle.mile.hint"), self.text())

    def test_both_word_orders_are_accepted(self):
        player = player_at("mile")
        self.run_input(["north", "If you ask nicely the gate opens!", "quit"],
                       lambda: main.explore(player, "mile"))
        self.assertIn(t("puzzle.open"), self.text())
        self.assertIn("The Crooked Mile", player["solved"])

    def test_answer_ignores_case_and_punctuation(self):
        self.assertEqual(main.normalise("  The GATE, opens!  "), "the gate opens")

    def test_archive_answer_is_me(self):
        player = player_at("archive")
        self.run_input(["north", "me", "quit"], lambda: main.explore(player, "archive"))
        self.assertIn(t("puzzle.open"), self.text())


class InputTests(GameTestCase):
    def test_out_of_range_number_is_rejected(self):
        party = [main.make_creature("claxon"), main.make_creature("mutter")]
        result = self.run_input(["0", "9", "abc", "2"], lambda: main.choose_creature(party, "Send out who?"))
        self.assertEqual(result, 1)

    def test_fainted_creature_cannot_be_chosen(self):
        party = [main.make_creature("claxon"), main.make_creature("mutter")]
        party[0]["hp"] = 0
        result = self.run_input(["1", "2"], lambda: main.choose_creature(party, "Send out who?"))
        self.assertEqual(result, 1)

    def test_bad_menu_choice_asks_again(self):
        self.run_input(["x", "4"], main.main)
        self.assertIn(t("menu.invalid"), self.text())

    def test_bad_combat_choice_does_not_use_a_turn(self):
        player = player_at("signpost")
        self.run_input(["9", "4"], lambda: main.fight(player, main.make_creature("mutter")))
        self.assertIn(t("combat.invalid"), self.text())

    def test_bad_word_choice_does_not_use_a_turn(self):
        player = player_at("signpost")
        self.run_input(["1", "7", "4"], lambda: main.fight(player, main.make_creature("mutter")))
        self.assertIn(t("combat.not_a_word"), self.text())


class FightTests(GameTestCase):
    def test_the_first_fight_explains_the_menu_only_once(self):
        player = player_at("signpost")
        self.run_input(["4"], lambda: main.fight(player, main.make_creature("mutter")))
        self.run_input(["4"], lambda: main.fight(player, main.make_creature("mutter")))
        self.assertEqual(self.text().count(t("combat.first_hint")), 1)

    def test_run_leaves_without_taking_damage(self):
        player = player_at("signpost")
        before = player["party"][0]["hp"]
        finished = self.run_input(["4"], lambda: main.fight(player, main.make_creature("mutter")))
        self.assertFalse(finished)
        self.assertEqual(player["party"][0]["hp"], before)

    def test_phrase_works_once_per_fight(self):
        player = player_at("signpost")
        self.run_input(["2", "2", "4"],
                       lambda: main.fight(player, main.make_creature("mutter")))
        self.assertIn(t("combat.phrase_spent"), self.text())

    def test_losing_the_last_creature_ends_the_fight(self):
        player = player_at("signpost", [main.make_creature("claxon")])
        player["party"][0]["hp"] = 1
        with mock.patch("main.random.randint", return_value=3):
            self.run_input(["1", "1", "4"],
                           lambda: main.fight(player, main.make_creature("silence")))
        self.assertIn(t("combat.no_words"), self.text())

    def test_winning_a_normal_fight_recruits(self):
        player = player_at("signpost", [main.make_creature("claxon")])
        foe = main.make_creature("mutter")
        foe["hp"] = 1
        with mock.patch("main.random.randint", return_value=0):
            self.run_input(["1", "1", "4"], lambda: main.fight(player, foe, True, False))
        self.assertEqual(len(player["party"]), 2)
        self.assertIn(t("combat.recruit", name=foe["name"]), self.text())

    def test_party_never_grows_past_the_limit(self):
        party = [main.make_creature("claxon") for _ in range(main.MAX_PARTY)]
        player = player_at("signpost", party)
        foe = main.make_creature("mutter")
        foe["hp"] = 1
        with mock.patch("main.random.randint", return_value=0):
            self.run_input(["1", "1", "4"], lambda: main.fight(player, foe, True, False))
        self.assertEqual(len(player["party"]), main.MAX_PARTY)


class SaveTests(GameTestCase):
    def test_save_and_load_round_trip(self):
        player = player_at("market")
        main.save_game(player, "market")
        loaded = main.load_game()
        self.assertEqual(loaded["name"], "Tester")
        self.assertEqual(loaded["spot"], "market")
        self.assertEqual(len(loaded["party"]), 2)

    def test_no_save_file_returns_none(self):
        self.assertIsNone(main.load_game())

    def test_continue_without_a_save_is_handled(self):
        self.run_input(["2", "4"], main.main)
        self.assertIn(t("save.none"), self.text())


class RestartTests(GameTestCase):
    def test_restart_raises(self):
        self.run_input(["restart"], lambda: self.assertRaises(main.RestartGame, main.ask))

    def test_restart_is_case_and_space_insensitive(self):
        self.run_input(["  RESTART  "], lambda: self.assertRaises(main.RestartGame, main.ask))

    def test_restart_from_the_title_returns_to_the_title(self):
        self.run_input(["restart", "4"], main.main)
        self.assertIn(t("system.restart"), self.text())

    def test_restart_mid_fight_returns_to_the_title(self):
        self.run_input(["1", "Ana", "1", "2", "fight", "restart", "4"], main.main)
        self.assertIn(t("system.restart"), self.text())

    def test_restart_mid_puzzle_returns_to_the_title(self):
        self.run_input(["1", "Ana", "1", "2", "north", "restart", "4"], main.main)
        self.assertIn(t("system.restart"), self.text())

    def test_name_is_not_restart(self):
        self.run_input(["1", "Restart", "1", "2", "quit", "4"], main.main)
        self.assertIn(t("area.signpost.name"), self.text())


if __name__ == "__main__":
    unittest.main()
