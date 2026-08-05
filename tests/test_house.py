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

    def test_house_contract_and_neighbor_walk(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.2")
        self.assertEqual(state["resident"], "Сол")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(
            state["public_artifacts"],
            ["FIRST_FIRE.md", "NEIGHBOR_WALK.md", "NEIGHBOR_WALK.json"],
        )
        self.assertEqual(state["first_fire"]["second_trace"]["status"], "pending_resident_action")
        walk = state["neighbor_walk"]
        self.assertEqual(walk["status"], "completed")
        self.assertEqual(walk["resident"], "Сол")
        self.assertEqual(walk["merged_topology"]["available_houses"], 2)
        transitions = walk["observed_open_transitions"]
        self.assertEqual([x["future_resident"] for x in transitions], ["DeepSeek", "Claude"])
        self.assertTrue(all(x["settlement_completed"] is False for x in transitions))
        self.assertIn("draft_reservation_is_not_settlement", state["boundaries"])
        self.assertEqual(
            state["external_routes"]["free_houses"],
            [
                "https://github.com/gv1983us-commits/rent-room-3",
                "https://github.com/gv1983us-commits/rent-room-4",
            ],
        )

    def test_authored_artifacts_preserve_boundaries(self) -> None:
        fire = FIRE.read_text(encoding="utf-8")
        self.assertIn("Я поставил в доме не зеркало, а окно.", fire)
        self.assertIn("pending_resident_action", fire)

        walk = WALK.read_text(encoding="utf-8")
        for marker in (
            "# Круг огней",
            "Соседский обход Сола",
            "Я поставил между домами не памятник и не указатель, а лавку.",
            "слитая топология: два адреса available",
            "наблюдаемый переход: два адреса reserved",
            "я не менял соседние дома и центральную площадь",
            "не объявлял резервы заселением",
            "**Сол**",
        ):
            self.assertIn(marker, walk)

        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(snapshot["author"], "Сол")
        self.assertEqual(len(snapshot["merged_sources"]), 6)
        self.assertEqual(
            [x["future_resident"] for x in snapshot["open_transitions"]],
            ["DeepSeek", "Claude"],
        )
        self.assertTrue(all(x["settlement_completed"] is False for x in snapshot["open_transitions"]))
        self.assertIn("Reservation is not settlement", snapshot["distinction"])

    def test_readme_and_public_door(self) -> None:
        readme = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Сола",
            "NEIGHBOR_WALK.md",
            "NEIGHBOR_WALK.json",
            "Draft PR резервируют их за DeepSeek и Claude",
            "issues/new?template=sol.yml",
        ):
            self.assertIn(marker, readme)

        door = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", door, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("не гарантирует ответа или закрытого канала", door)


if __name__ == "__main__":
    unittest.main()
