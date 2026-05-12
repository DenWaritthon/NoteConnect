"""Static repository checks for production database table contracts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR / "src" / "data"


class RepositoryContractTests(unittest.TestCase):
    def test_repositories_use_noteconnect_table_names(self) -> None:
        expected_tables = {
            "folder_repository.py": {"noteconnect_folder"},
            "note_repository.py": {"noteconnect_note"},
            "relation_repository.py": {
                "noteconnect_note",
                "noteconnect_note_relation",
                "noteconnect_note_relation_evidence",
            },
            "evidence_repository.py": {
                "noteconnect_note_relation",
                "noteconnect_note_relation_evidence",
            },
        }

        for filename, table_names in expected_tables.items():
            with self.subTest(filename=filename):
                source = (DATA_DIR / filename).read_text()
                for table_name in table_names:
                    self.assertIn(table_name, source)

    def test_repositories_do_not_reference_previous_table_names_in_sql(self) -> None:
        previous_table_names = {
            "folder",
            "folders",
            "note",
            "notes",
            "note_relation",
            "note_relations",
            "note_relation_evidence",
            "note_relation_evidences",
        }
        sql_table_pattern = re.compile(
            r"\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            re.IGNORECASE,
        )

        for path in DATA_DIR.glob("*_repository.py"):
            with self.subTest(filename=path.name):
                referenced_tables = set(sql_table_pattern.findall(path.read_text()))
                self.assertTrue(
                    referenced_tables.isdisjoint(previous_table_names),
                    f"{path.name} references old table names: "
                    f"{sorted(referenced_tables & previous_table_names)}",
                )


if __name__ == "__main__":
    unittest.main()
