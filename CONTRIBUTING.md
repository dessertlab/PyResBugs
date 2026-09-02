# Contributing a bug

PyResBugs accepts residual Python bugs with a public source repository and an identifiable fix commit. The command-line framework makes the binary workbook reproducible and checks contributions before review.

## Set up the framework

```console
git clone https://github.com/dessertlab/PyResBugs.git
cd PyResBugs
python -m pip install -e ".[test]"
pyresbugs validate
```

## Create and add a record

Start from a fix commit. The scaffold command caches a mirror of the source repository and fills the commit message, full SHA, URL, project name, and patch:

```console
pyresbugs scaffold \
  --repo https://github.com/OWNER/PROJECT \
  --commit FIX_COMMIT \
  --output bug.json
```

Complete every empty annotation in `bug.json`. The field contract is documented by [`schema/bug.schema.json`](schema/bug.schema.json), and a blank example is available at [`examples/bug.template.json`](examples/bug.template.json).

Preview the operation, add the record atomically, and validate the complete workbook:

```console
pyresbugs add bug.json --dry-run
pyresbugs add bug.json
pyresbugs validate
```

Commit both `PyresBugs.xlsx` and the framework/documentation changes relevant to the contribution. In the pull request, explain why the bug is residual, identify the fault acronym, and link the upstream fix or report. Do not include credentials, private source code, or generated repository caches.

## Verify checkout

Find the newly assigned content-derived ID and verify both revisions:

```console
pyresbugs query --commit FIX_COMMIT
pyresbugs checkout PB-ID --version buggy --work-dir ../project-buggy
pyresbugs checkout PB-ID --version fixed --work-dir ../project-fixed
```

The fixed revision is the recorded commit. The buggy revision defaults to its first parent; use `--parent N` when a merge commit requires a different parent.

