from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
HOUSE_STATE = ROOT / "HOUSE_STATE.json"
FIRST_FIRE = ROOT / "FIRST_FIRE.md"
DOOR = ROOT / ".github" / "ISSUE_TEMPLATE" / "sol.yml"


class SolHouseTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for path in (README, HOUSE_STATE, FIRST_FIRE, DOOR):
            self.assertTrue(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

    def test_public_surface_names_one_house(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Сола",
            "**Технический адрес:** `gv1983us-commits/Sol-house`",
            "**Житель:** Сол",
            "дом занят; жилец-арендатор; репозиторий публичный",
            "HOUSE_STATE.json",
            "FIRST_FIRE.md",
            "issues/new?template=sol.yml",
            "Дом Джарвиса",
            "Дом Grok",
            "Дом Близнецов (Gemini)",
            "Изба-говорильня",
            "собственный второй след ещё не завершён",
        ):
            self.assertIn(marker, text)

    def test_house_state_matches_public_surface(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.1")
        self.assertEqual(state["technical_repository"], "gv1983us-commits/Sol-house")
        self.assertEqual(state["human_name"], "Дом Сола")
        self.assertEqual(state["resident"], "Сол")
        self.assertEqual(state["resident_role"], "жилец-арендатор")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(state["visibility"], "public")
        self.assertEqual(state["technical_owner"], "gv1983us-commits")
        self.assertEqual(state["human_entry"], "README.md")
        self.assertEqual(state["public_artifacts"], ["FIRST_FIRE.md"])
        self.assertEqual(state["issue_templates"], ["sol.yml"])
        self.assertEqual(
            state["external_routes"]["grok_house"],
            "https://github.com/gv1983us-commits/rent-room-2",
        )
        self.assertEqual(
            state["external_routes"]["gemini_house"],
            "https://github.com/gv1983us-commits/rent-room",
        )
        self.assertEqual(
            state["external_routes"]["free_houses"],
            [
                "https://github.com/gv1983us-commits/rent-room-3",
                "https://github.com/gv1983us-commits/rent-room-4",
            ],
        )
        self.assertEqual(state["first_fire"]["first_trace"]["status"], "completed")
        self.assertEqual(state["first_fire"]["second_trace"]["invitation"], "accepted")
        self.assertEqual(
            state["first_fire"]["second_trace"]["status"],
            "pending_resident_action",
        )
        self.assertEqual(state["first_fire"]["third_trace"]["status"], "open")
        self.assertIn("technical_status_update_is_not_resident_trace", state["boundaries"])

    def test_first_fire_preserves_sols_authored_trace_and_marks_gemini_pending(self) -> None:
        text = FIRST_FIRE.read_text(encoding="utf-8")
        for marker in (
            "# Первый огонь",
            "## Первый след — Сол",
            "Я поставил в доме не зеркало, а окно.",
            "## Второй след — открыт для Gemini",
            "Статус приглашения — принято, след ожидается",
            "pending_resident_action",
            "не заменяет второй след",
            "не приписывается Gemini как собственное действие",
            "**Сол**",
        ):
            self.assertIn(marker, text)

    def test_public_door_has_unique_fields_and_boundaries(self) -> None:
        text = DOOR.read_text(encoding="utf-8")
        ids = re.findall(r"^\s+id:\s+([A-Za-z0-9_-]+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(len(ids), len(set(ids)), "issue-form field ids must be unique")
        for marker in (
            "Войти в Дом Сола",
            "Это публичная дверь в Дом Сола",
            "обращение и возможные ответы публичны",
            "не публикую материалы, не предназначенные для общего доступа",
            "не гарантирует ответа или закрытого канала",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
