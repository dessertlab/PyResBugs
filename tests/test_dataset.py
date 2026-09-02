from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import sample_record

from pyresbugs.dataset import (
    AmbiguousSelectorError,
    Dataset,
    DatasetError,
    InvalidRecordError,
    load_record_file,
)


def test_query_resolve_and_stable_id(workbook_path: Path) -> None:
    with Dataset(workbook_path) as dataset:
        records = dataset.query(project="PROJ", fault="mfc")
        assert len(records) == 2
        first = records[0]
        assert dataset.resolve(first.id).excel_row == 2
        assert dataset.resolve(first.id[3:11]).id == first.id
        assert dataset.resolve("1").id == first.id
        assert dataset.resolve("2222222").ordinal == 2

        old_id = first.id
        _, updated = dataset.update(first.id, {"Bug_Description": "Clearer text"})
        assert updated.id == old_id


def test_ambiguous_commit_requires_bug_id(workbook_path: Path) -> None:
    with Dataset(workbook_path) as dataset:
        dataset.add(
            sample_record(
                **{
                    "Fixed_Method": "another_method()",
                    "Faulty Code": "another failure",
                }
            )
        )
        with pytest.raises(AmbiguousSelectorError):
            dataset.resolve("1111111")


def test_add_update_remove_and_atomic_save(workbook_path: Path, tmp_path: Path) -> None:
    backup = tmp_path / "backup.xlsx"
    with Dataset(workbook_path) as dataset:
        added = dataset.add(
            sample_record(
                Commit_sha="3333333333333333333333333333333333333333",
                Commit_URL="https://github.com/example/project/commit/3333333333333333333333333333333333333333",
                **{"Fixed_Method": "third()", "Faulty Code": "third failure"},
            )
        )
        dataset.save(backup=backup)
    assert backup.is_file()

    with Dataset(workbook_path) as dataset:
        assert len(dataset) == 3
        original, updated = dataset.update(added.id, {"Fault_Acronym": "MIFS"})
        assert original.id != updated.id
        dataset.remove(updated.id)
        dataset.save()

    with Dataset(workbook_path) as dataset:
        assert len(dataset) == 2
        assert dataset.validate() == []


def test_rejects_invalid_and_duplicate_records(workbook_path: Path) -> None:
    with Dataset(workbook_path) as dataset:
        with pytest.raises(InvalidRecordError, match="Commit_sha"):
            dataset.add(sample_record(Commit_sha="not-a-sha"))
        with pytest.raises(InvalidRecordError, match="already in the dataset"):
            dataset.add(sample_record())


def test_refuses_to_save_invalid_workbook(workbook_path: Path) -> None:
    with Dataset(workbook_path) as dataset:
        dataset.sheet.cell(2, 5, "not-a-sha")
        with pytest.raises(DatasetError, match="refusing to save an invalid dataset"):
            dataset.save()


def test_load_record_file_accepts_exported_id(tmp_path: Path) -> None:
    path = tmp_path / "record.json"
    path.write_text(json.dumps({"Bug_ID": "PB-DEADBEEF", **sample_record()}), encoding="utf-8")
    loaded = load_record_file(path)
    assert "Bug_ID" not in loaded
    assert loaded["Project"] == "project"
