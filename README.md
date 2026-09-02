# PyResBugs

**PyResBugs** is a curated dataset containing **5007 residual Python bugs**, paired with their corresponding fixed versions and multi-level natural language (NL) descriptions. It is the first dataset designed specifically for **natural language-driven fault injection**, enabling advanced research in software testing and automated fault analysis.

---

## Description

Residual bugs are defects that remain undetected during traditional testing but surface later in production. **PyResBugs** focuses exclusively on these elusive faults, collected from prominent Python open-source projects. Each bug in the dataset is accompanied by:

- The faulty and fixed versions of the code.
- Three levels of NL descriptions:
  - **Implementation-Level Descriptions**: Technical and detailed, specifying the exact code changes.
  - **Contextual-Level Descriptions**: Abstracting the mechanism and impact of the fault.
  - **High-Level Descriptions**: Conceptual fault descriptions without technical specifics.

### Dataset Highlights

- **5007 residual bug pairs** from real-world Python projects.
- Annotations created and validated by domain experts.
- Supports the use of AI-driven models for fault injection, fault repairing, and software robustness studies in general.

You can find more details on the dataset in the accompanying paper.

---

## Versions

### Version 1: PyResBugs
This dataset includes 5007 pairs of faulty and fault-free code snippets collected from major Python frameworks. Each fault is enriched with NL descriptions to make fault injection accessible and realistic. This version is the foundation for developing AI-based fault analysis tools and advancing automated software testing research.

Future versions will expand the dataset with additional bugs, categories, and extended metadata.

---

## Command-line framework

PyResBugs includes a cross-platform Python CLI for querying the dataset, managing records, and checking out the source repository at a buggy or fixed revision. It follows the familiar `info`, `query`, and `checkout` workflow used by established bug benchmarks while retaining `PyresBugs.xlsx` as the dataset file.

Install it from a clone:

```console
python -m pip install -e ".[test]"
pyresbugs validate
pyresbugs info
```

### Find and inspect bugs

```console
pyresbugs projects
pyresbugs query --project b2-sdk --fault MFC
pyresbugs info PB-BUG-ID
pyresbugs export --format json --output PyresBugs.json
```

Each row receives a `PB-…` identifier derived from its project, fix commit, method, fault acronym, and faulty code. The identifier is independent of workbook order, so adding or removing other rows does not change it. A unique commit prefix or the current one-based record number can also be used as a selector.

### Check out source revisions

```console
pyresbugs checkout PB-BUG-ID --version buggy --work-dir ../buggy
pyresbugs checkout PB-BUG-ID --version fixed --work-dir ../fixed
```

Source repositories are stored as reusable local mirrors. The fixed version is the recorded fix commit, and the buggy version is its first parent by default. For a merge fix, select another parent with `--parent N`. Every checkout includes a `.pyresbugs.json` manifest with the resolved revisions and relevant dataset metadata.

### Add, update, and remove records

```console
# Prefill commit metadata and its patch, then complete the annotations.
pyresbugs scaffold --repo https://github.com/OWNER/PROJECT \
  --commit FIX_COMMIT --output bug.json

pyresbugs add bug.json --dry-run
pyresbugs add bug.json
pyresbugs update PB-BUG-ID changes.json
pyresbugs remove PB-BUG-ID --dry-run
pyresbugs remove PB-BUG-ID --yes --backup PyresBugs.before-remove.xlsx
pyresbugs validate
```

Workbook changes use an atomic replacement, and mutating commands support an optional backup. See [CONTRIBUTING.md](CONTRIBUTING.md) and the machine-readable [bug record schema](schema/bug.schema.json) for the contribution workflow.

---

## Citation

If you use **PyResBugs** in your research or projects, please cite the following paper:

```bibtex
@INPROCEEDINGS{11052783,
  author={Cotroneo, Domenico and De Rosa, Giuseppe and Liguori, Pietro},
  booktitle={2025 IEEE/ACM Second International Conference on AI Foundation Models and Software Engineering (Forge)}, 
  title={PyResBugs: A Dataset of Residual Python Bugs for Natural Language-Driven Fault Injection}, 
  year={2025},
  volume={},
  number={},
  pages={146-150},
  keywords={Foundation models;Computer bugs;Natural languages;Software systems;Python;Testing;Software engineering;Residual Bugs;Dataset;Python;Fault Injection;Natural Language},
  doi={10.1109/Forge66646.2025.00024}
}
```

---

## License

This dataset is released under the **MIT License**, allowing free use, modification, and distribution, provided proper attribution is given.

---

## Contact

For questions or further information, please feel free to contact giuseppe.derosa20@unina.it

