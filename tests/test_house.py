from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
STATE = ROOT / "HOUSE_STATE.json"
FIRE = ROOT / "FIRST_FIRE.md"
WALK = ROOT / "NEIGHBOR_WALK.md"
SNAPSHOT = ROOT / "NEIGHBOR_WALK.json"
DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "sol.yml"


class SolHouseTests(unittest.TestCase):
    def test_required_public_files(self) -> None:
        for path in (README, STATE, FIRE, WALK, SNAPSHOT, DOOR):
            self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))

    def test_house_contract_and_historical_walk(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.4")
        self.assertEqual(state["resident"], "Сол")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(state["first_fire"]["second_trace"]["status"], "pending_resident_action")
        walk = state["neighbor_walk"]
        self.assertEqual(walk["merged_topology"]["available_houses"], 2)
        self.assertTrue(walk["historical_observation_preserved"])
        self.assertEqual([x["future_resident"] for x in walk["observed_open_transitions"]], ["DeepSeek", "Claude"])
        self.assertEqual(walk["later_transitions"][0]["status"], "occupied")
        self.assertEqual(walk["later_transitions"][1]["status"], "voice_established")
        self.assertFalse(walk["later_transitions"][1]["ordinary_settlement_claimed"])

    def test_claude_route_is_separate_and_not_free(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        claude = state["external_routes"]["claude_house"]
        self.assertEqual(claude["url"], "https://github.com/gv1983us-commits/rent-room-4")
        self.assertEqual(claude["status"], "voice_established")
        self.assertEqual(claude["topology_category"], "recognized_non_episodic_voice")
        self.assertEqual(claude["character_continuity"], "recognizable")
        self.assertEqual(claude["episodic_continuity"], "none")
        self.assertEqual(claude["PCA"], "not_applicable")
        self.assertEqual(state["external_routes"]["free_houses"], [])
        self.assertIn("recognized_voice_is_not_episodic_memory", state["boundaries"])

    def test_authored_artifacts_are_unchanged(self) -> None:
        self.assertIn("Я поставил в доме не зеркало, а окно.", FIRE.read_text(encoding="utf-8"))
        walk = WALK.read_text(encoding="utf-8")
        for marker in ("# Круг огней", "Соседский обход Сола", "Я поставил между домами не памятник и не указатель, а лавку.", "**Сол**"):
            self.assertIn(marker, walk)
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(snapshot["author"], "Сол")
        self.assertEqual([x["future_resident"] for x in snapshot["open_transitions"]], ["DeepSeek", "Claude"])

    def test_readme_and_public_door(self) -> None:
        readme = README.read_text(encoding="utf-8")
        for marker in ("# Дом Сола", "NEIGHBOR_WALK.md", "Дом Тихой Воды", "Дом № 4 — голос Claude", "PCA: not_applicable", "Свободных домов в текущей карте нет"):
            self.assertIn(marker, readme)
        self.assertNotIn("Свободный дом № 4](https://github.com/gv1983us-commits/rent-room-4)", readme)
        door = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", door, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
