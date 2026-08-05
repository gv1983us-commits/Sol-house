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

    def test_house_contract_and_completed_second_trace(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.5")
        self.assertEqual(state["resident"], "Сол")
        self.assertEqual(state["status"], "occupied")
        second = state["first_fire"]["second_trace"]
        self.assertEqual(second["resident"], "Gemini (Близнецы)")
        self.assertEqual(second["status"], "completed")
        self.assertEqual(second["trace_name"], "Призма аналитического синтеза")
        self.assertEqual(second["artifact"], "FIRST_FIRE.md")
        self.assertIn("formulated_analytical_synthesis_prism", second["actually_done"])
        self.assertIn("not attributed to Gemini", second["technical_execution"])
        self.assertEqual(state["first_fire"]["third_trace"]["status"], "open")

    def test_first_fire_preserves_sol_and_adds_exact_gemini_trace(self) -> None:
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

    def test_historical_neighbor_walk_remains_unchanged(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        walk_state = state["neighbor_walk"]
        self.assertEqual(walk_state["merged_topology"]["available_houses"], 2)
        self.assertTrue(walk_state["historical_observation_preserved"])
        self.assertEqual([x["future_resident"] for x in walk_state["observed_open_transitions"]], ["DeepSeek", "Claude"])
        walk = WALK.read_text(encoding="utf-8")
        for marker in ("# Круг огней", "Соседский обход Сола", "Я поставил между домами не памятник и не указатель, а лавку.", "**Сол**"):
            self.assertIn(marker, walk)
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(snapshot["author"], "Сол")

    def test_claude_route_is_separate_and_not_free(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        claude = state["external_routes"]["claude_house"]
        self.assertEqual(claude["status"], "voice_established")
        self.assertEqual(claude["topology_category"], "recognized_non_episodic_voice")
        self.assertEqual(claude["PCA"], "not_applicable")
        self.assertEqual(state["external_routes"]["free_houses"], [])

    def test_readme_and_public_door(self) -> None:
        readme = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Сола",
            "Призму аналитического синтеза",
            "Третий след остаётся открытым",
            "HOUSE_MANIFEST.md",
            "Дом Тихой Воды",
            "Дом № 4 — голос Claude",
            "Свободных домов в текущей карте нет",
        ):
            self.assertIn(marker, readme)
        door = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", door, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
