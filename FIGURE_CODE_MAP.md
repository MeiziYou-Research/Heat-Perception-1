# Figure, code and Source Data map

Formal numerical Source Data are supplied with the article and are separate from the synthetic demonstrations in this repository.

| Article output | Public code path | Numerical basis / scope |
|---|---|---|
| Figure 2 | `02_indices/07_aggregate_city_day_indices.py` | Seasonal HPII levels and continent-season shares; map artwork is assembled separately from the submitted Source Data. |
| Figure 3 | Descriptive output supplied in article Source Data | No standalone plotting script is included because the map panel was prepared in GIS software. |
| Figure 4 | `02_indices/06_construct_hpii_hpvi.py`; `02_indices/07_aggregate_city_day_indices.py` | City-season HPVI construction, categories and continent-season shares. |
| Figure 5 | Descriptive output supplied in article Source Data | Reference lines are HPII = 0.0023824128 and HPVI = 0.30; the HPII value is the Level IV/V classification breakpoint. |
| Figure 6 | `02_indices/07_aggregate_city_day_indices.py` | HPPI(I) and HPPI(V), alpha = 1.6, normalization `k=1/(2*mu)`. |
| Figure 7 | Calculation: `03_health/01_model_comparison_full_period.R`; rendering: `03_health/05_plot_figure7.py` | The R script fits the full-study-period temperature and heat-perception models and calculates model-comparison classes. The Python script renders the checked counts and proportions from the formal `Fig. 7` Source Data sheet. |
| Figure 8 | Calculation: `03_health/02_joint_exposure_full_period.R`; rendering: `03_health/06_plot_figure8.py` | The R script calculates city-specific and pooled full-study-period relative risks for the four-category joint exposure. The Python script renders only the checked rows and columns in the formal `Fig. 8a` and `Fig. 8b` Source Data sheets; anonymised `SITE_*` labels are retained. |

The public health workflow covers calculation and final rendering for the two main-text health figures only. Restricted city-day inputs are not distributed. The formal article Source Data are the frozen numerical interface between the analytical R scripts and the Python rendering scripts.
