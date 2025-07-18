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

