# Discover Data Note: Data Availability Draft

## Data availability

The data described in this Data Note can be freely and openly accessed on Zenodo under https://doi.org/10.5281/zenodo.20472964. Please see table 1 and references [Reference numbers] for details and links to the data.

## Table 1 draft

| Label | Name of data file/data set | File types (file extension) | Data repository and identifier (DOI or accession number) |
| --- | --- | --- | --- |
| Data file 1 | Benchmark instance catalogue | Comma-separated values file (.csv) | Zenodo, https://doi.org/10.5281/zenodo.20472964 |
| Data set 1 | Reproducibility package for GB-style redundant convolution arithmetic over extension fields | Python source files, YAML configuration files, CSV catalogue, Markdown documentation (.py, .yaml, .csv, .md) | Zenodo, https://doi.org/10.5281/zenodo.20472964 |

## Reference draft

Garcia Crespi F. Reproducibility package for GB-style redundant convolution arithmetic over extension fields. Zenodo. 2026. https://doi.org/10.5281/zenodo.20472964.

## If the repository is not archived with a DOI

Use this only if the journal accepts non-public data availability for the article type:

The datasets generated during and/or analysed during the current study are available from the corresponding author on reasonable request.

For the Discover Data Note template, this is probably insufficient because the template states that all data files/data sets need to be deposited in a recommended data repository.

## Repository-specific note

The study uses deterministic, code-generated benchmark instances and experiment outputs rather than third-party observational datasets. The local repository currently contains:

- `data/catalog/instances.csv`: benchmark instance catalogue.
- `configs/*.yaml`: experiment configurations and random seeds.
- `src/gbext/experiments/`: scripts that generate correctness, benchmark, sparse-modulus, break-even, and constant-time-proxy outputs.
- `docs/paper_mapping.md`: mapping between claims, code modules, tests, experiments, and output files.

https://github.com/fedeg-umh-es/GB-style

Because the journal asks for persistent dataset identifiers, use the full Zenodo DOI URL in the Data availability statement, Table 1, and reference list.
