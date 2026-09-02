from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from openpyxl import Workbook

from pyresbugs.dataset import HEADERS


def sample_record(**changes: Any) -> dict[str, Any]:
    record = {
        "Bug_Description": "Close a leaked resource",
        "Bug_Type": "resource leak",
        "CVE-ID": None,
        "Commit_URL": "https://github.com/example/project/commit/1111111111111111111111111111111111111111",
        "Commit_sha": "1111111111111111111111111111111111111111",
        "Dataset_input": "GitHub",
        "Diff_patch": "diff --git a/module.py b/module.py",
        "Fault Free Code": "resource.close()",
        "Faulty Code": "pass",
        "Fixed_Method": "close_resource()",
        "Impact": None,
        "Implementation-Level Description": "Add the missing close call.",
        "Contextual-Level Description": "Release an acquired resource.",
        "High-Level Description": "Prevent a resource leak.",
        "Project": "project",
        "Python_Version": "3.10.0",
        "Test_File_Path": "tests/test_module.py",
        "Url": "https://github.com/example/project",
        "Fault_Acronym": "MFC",
    }
    record.update(changes)
    return record


@pytest.fixture
def workbook_path(tmp_path: Path) -> Path:
    path = tmp_path / "PyresBugs.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "PyResBugs"
    sheet.append(list(HEADERS))
    first = sample_record()
    second = sample_record(
        Commit_sha="2222222222222222222222222222222222222222",
        Commit_URL="https://github.com/example/project/commit/2222222222222222222222222222222222222222",
        **{"Faulty Code": "return None", "Fixed_Method": "load_resource()"},
    )
    sheet.append([first[field] for field in HEADERS])
    sheet.append([second[field] for field in HEADERS])
    workbook.save(path)
    workbook.close()
    return path
