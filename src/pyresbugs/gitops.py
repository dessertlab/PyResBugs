from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .dataset import DatasetError, Record, empty_record


class GitError(DatasetError):
    pass


def default_cache_path() -> Path:
    configured = os.environ.get("PYRESBUGS_CACHE")
    if configured:
        return Path(configured).expanduser()
    local_app_data = os.environ.get("LOCALAPPDATA")
    if os.name == "nt" and local_app_data:
        return Path(local_app_data) / "PyResBugs" / "cache"
    return Path.home() / ".cache" / "pyresbugs"


def run_git(arguments: Sequence[str], *, cwd: Path | None = None) -> str:
    command = ["git", *arguments]
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as error:
        raise GitError("git is required but was not found on PATH") from error
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout).strip()
        raise GitError(f"git command failed: {' '.join(command)}\n{detail}") from error
    return result.stdout


class RepositoryCache:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root is not None else default_cache_path()

    def repository_path(self, url: str) -> Path:
        parsed = urlparse(url)
        stem = Path(parsed.path.rstrip("/")).name.removesuffix(".git") or "repository"
        safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", stem)
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
        return self.root / f"{safe_stem}-{digest}.git"

    def ensure(self, url: str, *, update: bool = True) -> Path:
        repository = self.repository_path(url)
        self.root.mkdir(parents=True, exist_ok=True)
        if repository.exists():
            if not (repository / "HEAD").is_file():
                raise GitError(f"cache path is not a Git mirror: {repository}")
            if update:
                run_git(["remote", "update", "--prune"], cwd=repository)
        else:
            run_git(["clone", "--mirror", url, str(repository)])
        return repository

    def resolve(self, repository: Path, revision: str) -> str:
        return run_git(["rev-parse", "--verify", f"{revision}^{{commit}}"], cwd=repository).strip()

    def parent(self, repository: Path, revision: str, number: int = 1) -> str:
        if number < 1:
            raise GitError("parent number must be at least 1")
        return self.resolve(repository, f"{revision}^{number}")

    def checkout(
        self,
        record: Record,
        *,
        version: str,
        work_dir: str | Path,
        parent: int = 1,
        update: bool = True,
        dataset_path: str | Path | None = None,
    ) -> dict[str, Any]:
        if version not in ("buggy", "fixed"):
            raise GitError("version must be 'buggy' or 'fixed'")
        url = str(record.values["Url"])
        repository = self.ensure(url, update=update)
        fixed = self.resolve(repository, str(record.values["Commit_sha"]))
        buggy = self.parent(repository, fixed, parent)
        revision = buggy if version == "buggy" else fixed

        target = Path(work_dir)
        if target.exists():
            if not target.is_dir():
                raise GitError(f"checkout target is not a directory: {target}")
            if any(target.iterdir()):
                raise GitError(f"checkout directory is not empty: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        run_git(["clone", "--no-checkout", str(repository), str(target)])
        run_git(["remote", "set-url", "origin", url], cwd=target)
        run_git(["checkout", "--detach", revision], cwd=target)

        manifest = {
            "bug_id": record.id,
            "project": record.values["Project"],
            "version": version,
            "revision": revision,
            "buggy_revision": buggy,
            "fixed_revision": fixed,
            "parent": parent,
            "repository": url,
            "python_version": record.values["Python_Version"],
            "test_file_path": record.values["Test_File_Path"],
            "dataset": str(Path(dataset_path).resolve()) if dataset_path else None,
        }
        (target / ".pyresbugs.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return manifest

    def scaffold(self, url: str, commit: str, *, update: bool = True) -> dict[str, Any]:
        repository = self.ensure(url, update=update)
        fixed = self.resolve(repository, commit)
        parent = self.parent(repository, fixed)
        message = run_git(["show", "-s", "--format=%B", fixed], cwd=repository).strip()
        patch = run_git(["diff", "--no-ext-diff", parent, fixed], cwd=repository)

        parsed = urlparse(url)
        project = Path(parsed.path.rstrip("/")).name.removesuffix(".git")
        commit_url = f"{url.rstrip('/').removesuffix('.git')}/commit/{fixed}"
        record = empty_record()
        record.update(
            {
                "Bug_Description": message,
                "Commit_URL": commit_url,
                "Commit_sha": fixed,
                "Dataset_input": "GitHub",
                "Diff_patch": patch,
                "Project": project,
                "Url": url,
            }
        )
        return record
