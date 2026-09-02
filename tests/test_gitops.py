from __future__ import annotations

from pathlib import Path

from conftest import sample_record

from pyresbugs.dataset import Record
from pyresbugs.gitops import RepositoryCache, run_git


def create_repository(path: Path) -> tuple[str, str]:
    path.mkdir()
    run_git(["init"], cwd=path)
    run_git(["config", "user.name", "PyResBugs Test"], cwd=path)
    run_git(["config", "user.email", "test@example.com"], cwd=path)
    source = path / "module.py"
    source.write_text("value = 'buggy'\n", encoding="utf-8")
    run_git(["add", "module.py"], cwd=path)
    run_git(["commit", "-m", "Add buggy behavior"], cwd=path)
    buggy = run_git(["rev-parse", "HEAD"], cwd=path).strip()
    source.write_text("value = 'fixed'\n", encoding="utf-8")
    run_git(["commit", "-am", "Fix the behavior"], cwd=path)
    fixed = run_git(["rev-parse", "HEAD"], cwd=path).strip()
    return buggy, fixed


def test_checkout_buggy_and_fixed_versions(tmp_path: Path) -> None:
    source = tmp_path / "source"
    buggy, fixed = create_repository(source)
    values = sample_record(
        Commit_sha=fixed,
        Commit_URL=f"https://example.test/commit/{fixed}",
        Url=source.as_uri(),
    )
    record = Record(values, 2)
    cache = RepositoryCache(tmp_path / "cache")

    fixed_manifest = cache.checkout(
        record, version="fixed", work_dir=tmp_path / "fixed", update=False
    )
    buggy_manifest = cache.checkout(
        record, version="buggy", work_dir=tmp_path / "buggy", update=False
    )

    assert fixed_manifest["revision"] == fixed
    assert buggy_manifest["revision"] == buggy
    assert (tmp_path / "fixed" / "module.py").read_text(encoding="utf-8") == "value = 'fixed'\n"
    assert (tmp_path / "buggy" / "module.py").read_text(encoding="utf-8") == "value = 'buggy'\n"
    assert (tmp_path / "fixed" / ".pyresbugs.json").is_file()


def test_scaffold_prefills_git_metadata(tmp_path: Path) -> None:
    source = tmp_path / "source"
    _, fixed = create_repository(source)
    cache = RepositoryCache(tmp_path / "cache")
    record = cache.scaffold(source.as_uri(), fixed, update=False)

    assert record["Commit_sha"] == fixed
    assert record["Bug_Description"] == "Fix the behavior"
    assert "-value = 'buggy'" in record["Diff_patch"]
    assert "+value = 'fixed'" in record["Diff_patch"]
    assert record["Project"] == "source"
