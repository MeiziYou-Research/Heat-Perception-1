# Authorized health-input schema

The two full-study-period health-analysis scripts expect an authorized city-day RDS file named `final_dat.rds`. The restricted records are not distributed in this repository. The Python figure scripts instead read the formal Nature Communications Source Data workbook and do not require `final_dat.rds`.

Required fields are:

| Field | Meaning | Expected form |
|---|---|---|
| `city` | Analysis-site identifier | Character; stable within site |
| `country` | Country used to define the warm-season sensitivity window | Character |
| `date` | Observation date | Date-compatible |
| `month` | Calendar month | Integer 1–12 |
| `dow` | Day-of-week adjustment variable | Factor-compatible |
| `holiday` | Holiday adjustment variable | Binary or factor-compatible |
| `temp` | Daily temperature exposure | Numeric |
| `pm25` | Daily particulate-matter covariate | Numeric |
| `heatPerception` | Daily number of heat-perception posts | Numeric, non-negative |
| `count` | Daily health-outcome count | Numeric, non-negative |
| `type` | Outcome family | `Death`, `Hospitlization`, or `Emergency department visit` as used in the frozen scripts |
| `class` | Outcome subgroup | Includes `all-cause`, age/sex groups and ICD classes where available |

The scripts derive `heatday` from the within-city 95th percentile of `temp` and derive `percep2` as the binary daily heat-perception indicator (`heatPerception > 0`). Thus `percep2 = 1` means at least one heat-perception post was observed on that city-day; it is not a continuous HPII measure.

The shared R scripts implement the full-study-period primary analysis used for main-text Figures 7 and 8. No real city-day records or participant-level data are included in the public repository.
