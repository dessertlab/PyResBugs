from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, TextIO

from .dataset import (
    HEADERS,
    Dataset,
    DatasetError,
    Record,
    empty_record,
    load_record_file,
)
from .gitops import RepositoryCache, default_cache_path


def default_dataset_path() -> Path:
    configured = os.environ.get("PYRESBUGS_DATASET")
    if configured:
        return Path(configured).expanduser()
    local = Path.cwd() / "PyresBugs.xlsx"
    if local.is_file():
        return local
    repository_copy = Path(__file__).resolve().parents[2] / "PyresBugs.xlsx"
    return repository_copy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyresbugs",
        description="Query, maintain, and check out bugs from PyResBugs.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=default_dataset_path(),
        help="path to PyresBugs.xlsx (default: repository copy or PYRESBUGS_DATASET)",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)

    info = commands.add_parser("info", help="show dataset or bug information")
    info.add_argument("bug", nargs="?", help="bug ID, ordinal, or unique commit prefix")

    query = commands.add_parser("query", help="filter and list bug metadata")
    query.add_argument("--project", help="case-insensitive project substring")
    query.add_argument("--fault", help="exact fault acronym")
    query.add_argument("--commit", help="commit SHA prefix")
    query.add_argument("--limit", type=positive_int, default=20)
    query.add_argument("--format", choices=("table", "json", "csv"), default="table")

    commands.add_parser("projects", help="list project IDs and bug counts")
    commands.add_parser("validate", help="validate the workbook schema and records")

    export = commands.add_parser("export", help="export all records to JSON or CSV")
    export.add_argument("--format", choices=("json", "csv"), required=True)
    export.add_argument("--output", "-o", type=Path, help="output file (default: stdout)")

    template = commands.add_parser("template", help="write an empty bug JSON template")
    template.add_argument("--output", "-o", type=Path, help="output file (default: stdout)")

    scaffold = commands.add_parser(
        "scaffold", help="prefill a bug JSON file from a repository fix commit"
    )
    scaffold.add_argument("--repo", required=True, help="source repository URL")
    scaffold.add_argument("--commit", required=True, help="fix commit SHA")
    scaffold.add_argument("--output", "-o", type=Path, required=True)
    scaffold.add_argument("--cache", type=Path, default=default_cache_path())
    scaffold.add_argument(
        "--no-update", action="store_true", help="do not update an existing mirror"
    )

    add = commands.add_parser("add", help="append a bug from a JSON record")
    add.add_argument("record", type=Path)
    add.add_argument("--dry-run", action="store_true")
    add.add_argument("--backup", type=Path)

    update = commands.add_parser("update", help="update a bug from a partial JSON object")
    update.add_argument("bug", help="bug ID, ordinal, or unique commit prefix")
    update.add_argument("record", type=Path)
    update.add_argument("--dry-run", action="store_true")
    update.add_argument("--backup", type=Path)

    remove = commands.add_parser("remove", help="remove one bug from the workbook")
    remove.add_argument("bug", help="bug ID, ordinal, or unique commit prefix")
    remove.add_argument("--yes", action="store_true", help="confirm permanent removal")
    remove.add_argument("--dry-run", action="store_true")
    remove.add_argument("--backup", type=Path)

    checkout = commands.add_parser(
        "checkout", help="clone and check out a buggy or fixed project revision"
    )
    checkout.add_argument("bug", help="bug ID, ordinal, or unique commit prefix")
    checkout.add_argument("--version", "-v", choices=("buggy", "fixed", "b", "f"), required=True)
    checkout.add_argument("--work-dir", "-w", type=Path, required=True)
    checkout.add_argument("--parent", type=positive_int, default=1)
    checkout.add_argument("--cache", type=Path, default=default_cache_path())
    checkout.add_argument(
        "--no-update", action="store_true", help="do not update an existing mirror"
    )
    return parser


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "template":
            write_json(empty_record(), args.output)
            return 0
        if args.command == "scaffold":
            if args.output.exists():
                raise DatasetError(f"output file already exists: {args.output}")
            cache = RepositoryCache(args.cache)
            record = cache.scaffold(args.repo, args.commit, update=not args.no_update)
            write_json(record, args.output)
            print(f"Wrote annotation scaffold to {args.output}")
            return 0

        with Dataset(args.dataset) as dataset:
            if args.command == "info":
                return command_info(dataset, args.bug)
            if args.command == "query":
                records = dataset.query(project=args.project, fault=args.fault, commit=args.commit)
                render_records(records[: args.limit], args.format, sys.stdout)
                if len(records) > args.limit:
                    print(
                        f"Showing {args.limit} of {len(records)} matches; use --limit to see more.",
                        file=sys.stderr,
                    )
                return 0
            if args.command == "projects":
                rows = [
                    {"Project": project, "Bugs": count}
                    for project, count in sorted(dataset.projects().items())
                ]
                print_table(rows, ("Project", "Bugs"), sys.stdout)
                return 0
            if args.command == "validate":
                issues = dataset.validate()
                for issue in issues:
                    print(issue)
                errors = sum(issue.level == "error" for issue in issues)
                if errors:
                    print(f"Validation failed with {errors} error(s).")
                    return 1
                print(f"Valid {len(dataset):,}-bug dataset at {dataset.path}")
                return 0
            if args.command == "export":
                return command_export(dataset, args.format, args.output)
            if args.command == "add":
                record = dataset.add(load_record_file(args.record))
                if not args.dry_run:
                    dataset.save(backup=args.backup)
                suffix = " (dry run)" if args.dry_run else ""
                print(f"Added {record.id} at record {record.ordinal}{suffix}")
                return 0
            if args.command == "update":
                original, updated = dataset.update(args.bug, load_record_file(args.record))
                if not args.dry_run:
                    dataset.save(backup=args.backup)
                suffix = " (dry run)" if args.dry_run else ""
                print(f"Updated {original.id} -> {updated.id}{suffix}")
                return 0
            if args.command == "remove":
                if not args.yes and not args.dry_run:
                    raise DatasetError("removal requires --yes (or use --dry-run)")
                record = dataset.remove(args.bug)
                if not args.dry_run:
                    dataset.save(backup=args.backup)
                suffix = " (dry run)" if args.dry_run else ""
                print(f"Removed {record.id} ({record.values['Project']}){suffix}")
                return 0
            if args.command == "checkout":
                record = dataset.resolve(args.bug)
                cache = RepositoryCache(args.cache)
                version = {"b": "buggy", "f": "fixed"}.get(args.version, args.version)
                manifest = cache.checkout(
                    record,
                    version=version,
                    work_dir=args.work_dir,
                    parent=args.parent,
                    update=not args.no_update,
                    dataset_path=dataset.path,
                )
                print(
                    f"Checked out {record.id} {version} revision "
                    f"{manifest['revision']} to {args.work_dir}"
                )
                return 0
    except DatasetError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 2


def command_info(dataset: Dataset, selector: str | None) -> int:
    if selector is None:
        projects = dataset.projects()
        print(f"Dataset: {dataset.path}")
        print(f"Bugs: {len(dataset):,}")
        print(f"Projects: {len(projects):,}")
        print(f"Fault types: {len({r.values['Fault_Acronym'] for r in dataset.records()}):,}")
        return 0
    record = dataset.resolve(selector)
    print(json.dumps(record.as_dict(), ensure_ascii=False, indent=2))
    return 0


def command_export(dataset: Dataset, format_name: str, output: Path | None) -> int:
    stream: TextIO
    should_close = output is not None
    if output is None:
        stream = sys.stdout
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        stream = output.open("w", encoding="utf-8", newline="")
    try:
        if format_name == "json":
            dataset.export_json(stream)
        else:
            dataset.export_csv(stream)
    finally:
        if should_close:
            stream.close()
    if output:
        print(f"Exported {len(dataset):,} bugs to {output}")
    return 0


def render_records(records: list[Record], format_name: str, output: TextIO) -> None:
    if format_name == "json":
        json.dump([record.as_dict() for record in records], output, ensure_ascii=False, indent=2)
        output.write("\n")
        return
    if format_name == "csv":
        writer = csv.DictWriter(output, fieldnames=("Bug_ID", *HEADERS), lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow(record.as_dict())
        return
    rows = [
        {
            "Bug_ID": record.id,
            "Project": record.values["Project"],
            "Commit": str(record.values["Commit_sha"])[:12],
            "Fault": record.values["Fault_Acronym"],
            "Method": record.values["Fixed_Method"],
        }
        for record in records
    ]
    print_table(rows, ("Bug_ID", "Project", "Commit", "Fault", "Method"), output)


def print_table(rows: list[dict[str, Any]], fields: Sequence[str], output: TextIO) -> None:
    if not rows:
        print("No matches.", file=output)
        return
    rendered = [{field: truncate(str(row.get(field, "")), 60) for field in fields} for row in rows]
    widths = {field: max(len(field), *(len(row[field]) for row in rendered)) for field in fields}
    print("  ".join(field.ljust(widths[field]) for field in fields), file=output)
    print("  ".join("-" * widths[field] for field in fields), file=output)
    for row in rendered:
        print("  ".join(row[field].ljust(widths[field]) for field in fields), file=output)


def truncate(value: str, limit: int) -> str:
    single_line = " ".join(value.splitlines())
    return single_line if len(single_line) <= limit else single_line[: limit - 3] + "..."


def write_json(values: dict[str, Any], output: Path | None) -> None:
    content = json.dumps(values, ensure_ascii=False, indent=2) + "\n"
    if output is None:
        print(content, end="")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


def entrypoint() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    entrypoint()
