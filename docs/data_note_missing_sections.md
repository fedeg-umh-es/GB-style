# Missing Sections for `Data-note-template-filled.docx`

Copy these sections into the Discover Data Note template and delete the blue template instructions.

## Title

Reproducibility package for GB-style redundant convolution arithmetic over extension fields

## Author details

Federico Garcia Crespi  
[Institutional affiliation]  
[Institutional address]  
Corresponding author: [email address]

## Abstract

### Objectives

This Data Note describes a reproducibility package created to support computational experiments on GB-style redundant convolution arithmetic over extension fields. The package was generated to make the benchmark instances, configuration files, source code, tests, and documentation associated with the study reusable and auditable.

### Data description

The data consist of a curated benchmark instance catalogue and a complete reproducibility package containing Python source code, YAML configuration files, tests, and documentation. The package includes deterministic experiment settings for correctness checks, benchmark matrices, sparse-modulus studies, break-even analyses, and constant-time proxy studies. The files are deposited on Zenodo under https://doi.org/10.5281/zenodo.20472964.

## Objective

The objective of this Data Note is to describe and make available the reproducibility package for computational experiments on GB-style redundant convolution arithmetic over extension fields. The package was prepared to support transparent reuse of the benchmark catalogue, implementation code, configuration files, and experiment structure used in the associated study.

The deposited material is intended to help other researchers inspect the experimental setup, reproduce the computational workflows, and adapt the benchmark structure for related studies in finite-field and polynomial arithmetic. The package contains deterministic benchmark instances and configuration files rather than observational or human-subject data.

## Data description

Data set 1 contains the reproducibility package for GB-style redundant convolution arithmetic over extension fields. The package includes Python source files, YAML configuration files, a CSV benchmark catalogue, tests, and Markdown documentation.

The benchmark catalogue is provided as `data/catalog/instances.csv`. It defines experiment instances by field degree, polynomial degree, field modulus, ring-modulus family, modulus weight, modulus density, and notes describing the intended benchmark setting. The source code under `src/gbext/` implements finite-field arithmetic, baseline multiplication routines, GB-style multiplication routines, experiment drivers, analysis helpers, and command-line entry points. The configuration files under `configs/` define deterministic seeds, field parameters, polynomial degrees, benchmark methods, trial counts, warm-up settings, and constant-time proxy settings.

The deposited package also includes tests under `tests/` and project documentation under `docs/`. The file `docs/paper_mapping.md` maps theoretical, algorithmic, and empirical claims to the corresponding code modules, tests, experiments, and expected output files. Experiment outputs are designed to be generated reproducibly from the deposited code and configurations.

No third-party observational data are included. The package is composed of deterministic, code-generated benchmark definitions and reproducibility materials.

## Limitations

- The package provides computational benchmark definitions and reproducibility code, not observational measurements from an external environment.
- Timing-related outputs may vary across hardware, operating systems, Python versions, and local runtime conditions.
- Constant-time proxy measurements are algorithmic diagnostics and do not constitute a hardware-level side-channel security proof.
- The benchmark scope is limited to the field sizes, polynomial degrees, modulus families, and methods represented in the deposited configurations.

## Abbreviations

CSV: comma-separated values.  
DOI: digital object identifier.  
GB: ghost bit.  
YAML: YAML Ain't Markup Language.

## Acknowledgments

Not applicable.

## Funding

[Confirm one option before submission.]

Option A:
This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

Option B:
This work was supported by [funding body] under grant number [grant number].

## Author contributions

Federico Garcia Crespi conceptualized the study, designed the computational experiments, implemented the software, prepared the reproducibility package, and wrote the Data Note.

## Competing interests

The author declares no competing interests.

## Ethics approval

Not applicable.

## Consent to participate

Not applicable.

## Consent to publish

Not applicable.

## Data availability

The data described in this Data Note can be freely and openly accessed on Zenodo under https://doi.org/10.5281/zenodo.20472964. Please see table 1 and references [1] for details and links to the data.

## Code availability

The source code associated with this Data Note is included in the Zenodo record at https://doi.org/10.5281/zenodo.20472964 and is also available from the GitHub repository: https://github.com/fedeg-umh-es/GB-style.

## References

[1] Garcia Crespi F. Reproducibility package for GB-style redundant convolution arithmetic over extension fields. Zenodo. 2026. https://doi.org/10.5281/zenodo.20472964.

## Table 1

| Label | Name of data file/data set | File types (file extension) | Data repository and identifier (DOI or accession number) |
| --- | --- | --- | --- |
| Data set 1 | Reproducibility package for GB-style redundant convolution arithmetic over extension fields | Python source files, YAML configuration files, CSV catalogue, Markdown documentation (.py, .yaml, .csv, .md) | Zenodo, https://doi.org/10.5281/zenodo.20472964 |

## Fields still requiring confirmation

- Institutional affiliation.
- Institutional address.
- Corresponding author email.
- Funding statement.
