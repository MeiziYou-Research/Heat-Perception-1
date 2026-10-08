# Global Seasonal Dynamics of Public Heat Perception Across Cities and Associated Health Signals

**Manuscript:** You, M. et al. (2026). Global seasonal dynamics of public heat perception across cities and associated health signals. *Nature Communications*.

This repository contains the shared analysis and figure-generation code supporting the manuscript, including the main full-study-period health analyses for Figures 7 and 8. It is organised into three modules, each with its own README, software requirements and, where appropriate, fully synthetic demonstration data.

## Repository structure

```text
01_BERT/
├── README.md
├── requirements.txt
├── 01_data_collection_stub.py
├── 02_candidate_retrieval.py
├── 03_rule_filtering.py
├── 04_deduplicate_and_account_hygiene.py
├── 05_build_gold_labels.py
├── 06_train_grouped_cv.py
├── 07_validate_and_audit.py
└── sample_data/

02_indices/
├── README.md
├── requirements.txt
├── 01_construct_hpii_hpvi.py
├── 02_aggregate_city_day_indices.py
└── sample_data/

03_health/
├── README.md
├── requirements.txt
├── INPUT_SCHEMA.md
├── 01_model_comparison_full_period.R
├── 02_joint_exposure_full_period.R
├── 03_plot_figure7.py
└── 04_plot_figure8.py
```

## Module 1 — BERT training and heat-perception text analysis

**Code owners:** Meizi You, Xiyuan Ren  
**Data curation leads:** Meizi You, ChengHe Guan

This module identifies heat-perception posts through candidate retrieval, rule filtering, deduplication, labelled-data preparation, BERT fine-tuning, validation and audit export.

The repository includes 36 fully synthetic examples so that the shared workflow and input structure can be inspected without access to the original X/Twitter corpus. These examples contain no real posts, usernames, URLs, post identifiers or geographic identifiers and are not intended for scientific inference. See `01_BERT/README.md` for details.

**Software environment:** Python 3.9.24, pandas 2.0.3, NumPy 1.21.6, scikit-learn 1.5.0, PyTorch 2.2.1, Transformers 4.38.1 and NLTK 3.7. NLTK WordNet resources are optional.

## Module 2 — Heat-perception index construction

**Code owner:** Meizi You  
**Data curation lead:** Meizi You

This module constructs the Heat Perception Intensity Index (HPII), Heat Perception Variability Index (HPVI), and intensity- and variability-based Heat Perception Polarisation Index measures, HPPI(I) and HPPI(V). It also applies the fixed annual-reference HPII breaks to seasonal values and produces the city-season classifications used in the manuscript.

A small, fully synthetic demonstration dataset is included to illustrate the index workflow. It does not represent the 347 study cities or reproduce the study's geographic distribution or scientific results. See `02_indices/README.md` for details.

**Software environment:** Python 3.9.24, pandas 2.0.3 and NumPy 1.21.6.

## Module 3 — Main full-study-period health-outcome analyses

**Code owners:** Zhihu Xu, Meizi You  
**Data curation lead:** Yuming Guo

This module compares temperature-based and binary heat-perception models for emergency-department visits, hospitalisations and mortality, and estimates the health associations for the four joint-exposure categories used in the manuscript. It contains the full-study-period calculation code for Figures 7 and 8 and the corresponding Source Data-driven figure-rendering code.

Restricted health records are not included. The required input structure is documented in `03_health/INPUT_SCHEMA.md`; access to the underlying health data is governed by the respective data custodians and applicable data-sharing agreements. See `03_health/README.md` for details.

**Software environment:** R 4.3.3 with `dlnm` 2.4.7, `mixmeta` 1.2.2 and the listed supporting R packages. The final figure-rendering scripts use Python 3.9.24, pandas 2.0.3, Matplotlib 3.5.2 and openpyxl 3.1.5. Maps were prepared using ArcGIS Pro 3.1.6.

## Data availability

Raw X/Twitter text and the underlying city-day analytical records are not redistributed. The only study-derived numerical data released with this repository package are the rows and columns contained in the accompanying article `Source Data.xlsx`; no additional study-derived city-level records or variables are supplied through the GitHub repository. The included text and index demonstrations are fully synthetic and are not Nature Communications Source Data.

Restricted health-outcome data are available only subject to approval from the respective data custodians and applicable data-sharing agreements.

The formal numerical Source Data underlying the published figures are provided separately with the article in `Source Data.xlsx`. This workbook defines the public study-data boundary for the repository package.

## Reproducibility scope

The repository provides the custom analysis code, required input schemas and safe synthetic examples. It does not include a separate set of reference outputs. Because the original social-media and health datasets are restricted, the synthetic demonstrations illustrate code execution and data structure but do not reproduce the manuscript estimates; the numerical data supporting the figures are supplied in the article Source Data.

The mapping between manuscript figures, analysis scripts and formal Source Data is provided in `FIGURE_CODE_MAP.md`.

## License

This repository is released under the MIT License. See `LICENSE`.

## Contact

Meizi You: meizi.you2026@gmail.com
