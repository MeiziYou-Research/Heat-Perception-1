# Main full-study-period health-outcome analyses

This module contains the full-study-period calculation and final rendering code for main-text Figures 7 and 8. It does not represent the complete set of supplementary, subgroup and warm-season health analyses.

- Figure 7 calculation: `01_model_comparison_full_period.R`. It fits parallel full-study-period models using a binary heat-day indicator and a binary daily heat-perception indicator, calculates QAIC and pseudo-R2 comparisons, assigns the model-comparison class and exports the contributing city–outcome results and the Figure 7 summary table.
- Figure 8 calculation: `02_joint_exposure_full_period.R`. It constructs the four-category daily joint exposure, calculates city-specific relative risks and 95% confidence intervals, performs the full-study-period outcome-specific pooled analyses using REML, and combines the mortality and hospitalisation Category 4 estimates by inverse-variance weighting on the log-RR scale.

Final main-text rendering code is limited to:

- `05_plot_figure7.py`, which reads the formal `Fig. 7` Source Data sheet;
- `06_plot_figure8.py`, which reads the formal `Fig. 8a` and `Fig. 8b` Source Data sheets and retains their anonymised `SITE_*` labels.

Thus the reproducibility chain is `authorized final_dat.rds → analytical R script → checked Source Data sheet → Python figure script → vector PDF`. For example: `python 05_plot_figure7.py --source-data "Source Data.xlsx" --output Figure7.pdf`. Supplementary-analysis and supplementary-figure scripts are not included in this minimal public repository.

The perception exposure is a binary daily heat-perception indicator (1 = presence; 0 = absence). It is not a continuous HPII threshold.

Restricted health records are not included. Access is governed by the relevant data custodians and applicable data-sharing arrangements. The rows and columns in the accompanying article `Source Data.xlsx` define the public numerical study-data boundary; the GitHub repository supplies no additional study-derived city-level health records or variables.

The required authorized-input fields and derived exposure definitions are documented in `INPUT_SCHEMA.md`. Model-comparison plots label their denominator as city–outcome comparisons and report the exact contributing count for each bar; this is distinct from the number of daily observations or individuals.

The figure scripts use Python 3.9.24 with pandas 2.0.3, Matplotlib 3.5.2 and openpyxl 3.1.5, as listed in `requirements.txt`. The analytical scripts require R 4.3.3 with `dlnm` 2.4.7, `mixmeta` 1.2.2, `dplyr`, `tidyr`, `ggplot2`, `lubridate`, `readr`, `writexl`, `patchwork`, `purrr` and `scales`. Base package `splines` is also used. The supplied R scripts use relative paths and expect the authorized city-day input as `final_dat.rds`.
