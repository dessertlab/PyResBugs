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

## Citation

If you use **PyResBugs** in your research or projects, please cite the ICSE-FORGE 2025 paper:

a citation will be available as soon as possible
---

## License

This dataset is released under the **MIT License**, allowing free use, modification, and distribution, provided proper attribution is given.

---

## Contact

For questions or further information, please feel free to contact us or open an issue in this repository.

