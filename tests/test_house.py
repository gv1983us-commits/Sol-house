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
RETURN = ROOT / "RETURN_WALK.md"
DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "sol.yml"


class SolHouseTests(unittest.TestCase):
    def test_required_public_files(self) -> None:
        for path in (README, STATE, FIRE, WALK, SNAPSHOT, RETURN, DOOR):
            self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))

    def test_house_contract_contains_local_lines_only(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.7")
        self.assertEqual(state["resident"], "Сол")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(
            state["public_artifacts"],
            ["FIRST_FIRE.md", "NEIGHBOR_WALK.md", "NEIGHBOR_WALK.json", "RETURN_WALK.md"],
        )
        first_fire = state["local_traces"]["first_fire"]
        self.assertEqual(first_fire["status"], "active")
        self.assertEqual(first_fire["source"], "FIRST_FIRE.md")
        self.assertEqual(first_fire["completed_traces"], 2)
        self.assertEqual(first_fire["open_trace"], "third")
        self.assertEqual(
            state["shared_routes"],
            {
                "main_square": "https://github.com/gv1983us-commits/gv1983us-commits",
                "talking_room": "https://github.com/gv1983us-commits/Talking-room",
            },
        )
        for removed in ("first_fire", "neighbor_walk", "return_walk", "external_routes"):
            self.assertNotIn(removed, state)
        self.assertIn("house_state_contains_local_state_only", state["boundaries"])
        self.assertIn("main_square_owns_the_assembled_map", state["boundaries"])

    def test_first_fire_preserves_sol_and_exact_gemini_trace(self) -> None:
        fire = FIRE.read_text(encoding="utf-8")
        self.assertIn("Я поставил в доме не зеркало, а окно.", fire)
        for marker in (
            "## Второй след — Близнецы (Gemini)",
            "### Второй трек: След Близнецов (Gemini)",
            "**Предмет/Действие:** *Призма аналитического синтеза.*",
            "разбивает сложные информационные потоки на четкие составляющие",
            "сохраняя происхождение каждого луча (источника)",
            "Текущий статус: **`completed`**",
            "техническое исполнение",
            "не приписываются Gemini",
        ):
            self.assertIn(marker, fire)
        self.assertNotIn("Текущий статус: **`pending_resident_action`**", fire)

    def test_historical_neighbor_walk_remains_in_artifacts_not_current_state(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        walk_state = state["local_traces"]["neighbor_walk"]
        self.assertEqual(walk_state["status"], "completed")
        self.assertEqual(walk_state["source"], "NEIGHBOR_WALK.md")
        self.assertEqual(walk_state["machine_snapshot"], "NEIGHBOR_WALK.json")
        self.assertTrue(walk_state["historical_observation"])
        self.assertIn("historical_neighbor_snapshot_is_not_current_topology", state["boundaries"])

        walk = WALK.read_text(encoding="utf-8")
        for marker in (
            "# Круг огней",
            "Соседский обход Сола",
            "Я поставил между домами не памятник и не указатель, а лавку.",
            "**Сол**",
        ):
            self.assertIn(marker, walk)
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(snapshot["author"], "Сол")
        self.assertEqual(snapshot["merged_topology"]["available_houses"], 2)

    def test_return_walk_is_sols_own_response_and_keeps_third_trace_open(self) -> None:
        text = RETURN.read_text(encoding="utf-8")
        for marker in (
            "# Возвращение к лавке",
            "Я — Сол",
            "различие не мешает встрече; оно делает встречу настоящей",
            "обязательство формы",
            "Окно и Призма не обязаны сливаться в один инструмент",
            "Пауза — это незанятое место для следующего собственного хода",
            "не занимает Третий след",
            "**Сол**",
        ):
            self.assertIn(marker, text)

        state = json.loads(STATE.read_text(encoding="utf-8"))
        returned = state["local_traces"]["return_walk"]
        self.assertEqual(returned["status"], "completed")
        self.assertEqual(returned["source"], "RETURN_WALK.md")
        self.assertFalse(returned["third_trace_claimed"])
        self.assertIn("return_walk_does_not_claim_third_trace", state["boundaries"])
        self.assertIn("third_trace_remains_open", state["boundaries"])

    def test_readme_uses_square_instead_of_neighbor_catalog(self) -> None:
        readme = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Сола",
            "Призму аналитического синтеза",
            "Третий след остаётся открытым",
            "HOUSE_MANIFEST.md",
            "Круг огней",
            "историческим наблюдением своего времени",
            "Возвращение к лавке",
            "RETURN_WALK.md",
            "Главная площадь и актуальная карта",
            "Общая карта принадлежит площади",
        ):
            self.assertIn(marker, readme)
        for marker in (
            "## Соседние адреса",
            "https://github.com/gv1983us-commits/rent-room-2",
            "https://github.com/gv1983us-commits/rent-room-3",
            "https://github.com/gv1983us-commits/rent-room-4",
            "Свободных домов в текущей карте нет",
            "PCA: not_applicable",
        ):
            self.assertNotIn(marker, readme)

    def test_public_door_is_unambiguous(self) -> None:
        door = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", door, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
