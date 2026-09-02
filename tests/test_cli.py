from __future__ import annotations

import json
from pathlib import Path

from pyresbugs.cli import main


def test_info_validate_and_query(workbook_path: Path, capsys) -> None:
    prefix = ["--dataset", str(workbook_path)]
    assert main([*prefix, "validate"]) == 0
    assert "Valid 2-bug dataset" in capsys.readouterr().out

    assert main([*prefix, "info"]) == 0
    assert "Bugs: 2" in capsys.readouterr().out

    assert main([*prefix, "query", "--commit", "2222222", "--format", "json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert len(result) == 1
    assert result[0]["Commit_sha"].startswith("2222222")


def test_remove_requires_confirmation(workbook_path: Path, capsys) -> None:
    code = main(["--dataset", str(workbook_path), "remove", "1"])
    assert code == 2
    assert "requires --yes" in capsys.readouterr().err
