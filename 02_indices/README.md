# Heat-perception index construction

The recorded environment uses Python 3.9.24, pandas 2.0.3 and NumPy 1.21.6. Install the exact package versions listed in `requirements.txt`.

The module has two explicit stages. `01_construct_hpii_hpvi.py` constructs city-season HPII and HPVI from restricted city-day counts. `02_aggregate_city_day_indices.py` applies the frozen classifications and calculates continent-season summaries and HPPI(I)/HPPI(V).

- HPII is calculated as the seasonal sum of heat-perception posts divided by the seasonal sum of eligible posts. A separate daily series is median-decentred within city-month and winsorised at the 1st and 99th percentiles for preprocessing diagnostics and sensitivity analyses.
- HPVI is the seasonal mean of trailing seven-day coefficients of variation in the completed daily heat-perception-post count series. Each rolling coefficient is the sample standard deviation divided by the corresponding rolling mean; no epsilon is added to the denominator.
- Seven seasonal HPII levels use fixed breaks derived once from the annual city-level reference distribution: `0.00114114902598386`, `0.00178543238369676`, `0.00216027065870402`, `0.00238241283234082`, `0.00280137357672149`, and `0.00884031425500674`.
- HPVI categories are Low (`<=0.15`), Moderate (`>0.15` and `<=0.30`) and High (`>0.30`).
- HPPI(I) and HPPI(V) use alpha `1.6` and normalization `k=1/(2*mu)`.
- Representative values are `(1,2,3,5,7,10,14)` for HPII levels and `(1,3,10)` for HPVI categories.

The descriptive guides `0.05` and `0.15` for HPPI are not inferential thresholds. Figure 5 uses reference lines at `HPII=0.0023824128` (the Level IV/V classification breakpoint) and `HPVI=0.30`.

## Input

The construction script accepts one city-day row per `city_id` and `date`, with `continent`, `hemisphere`, `heat_posts`, and `total_posts`. An optional event flag can be supplied with `--event-flag-col`; flagged days are excluded when estimating the city-month median but retain their observed values. Missing calendar days are completed only for the HPVI count series and their heat-perception-post counts are imputed using the city median.

The aggregation script accepts a long city-season CSV with `city_id`, `continent`, `season`, `HPII`, and `HPVI`. It verifies that every season contains the identical city set, that each city has one stable continent, that the expected continent count is present, and that index values are finite and within their valid domains. An optional annual reference CSV may contain `city_id` and `annual_HPII`; when supplied, its city identifiers must match the seasonal input exactly, while the frozen break values remain unchanged.

## Run

```bash
python 01_construct_hpii_hpvi.py --daily-input city_day_counts.csv --output-dir constructed_indices
python 02_aggregate_city_day_indices.py --seasonal-input constructed_indices/city_season_hpii_hpvi.csv --output-dir outputs
```

To use a named event indicator in the de-centering baseline:

```bash
python 01_construct_hpii_hpvi.py --daily-input city_day_counts.csv --output-dir constructed_indices --event-flag-col event_week
```

The construction stage exports the raw and normalized daily audit fields, the rolling-window HPVI fields, and the final city-season HPII/HPVI input consumed by the aggregation stage.

The aggregation stage can also be run directly from a frozen city-season input:

```bash
python 02_aggregate_city_day_indices.py --seasonal-input city_season.csv --output-dir outputs
```

For a public execution check using fully synthetic values:

```bash
python sample_data/generate_demo_indices.py
python 02_aggregate_city_day_indices.py --seasonal-input sample_data/demo_city_season.csv --output-dir demo_outputs --expect-cities 24 --expect-continents 6
```

The output includes classified city-season records, continent-season category shares, and 48 HPPI estimates (six continents x four seasons x two metrics) when the complete 347-city dataset is supplied.

The demonstration values are synthetic and are not intended for scientific inference. The demonstration identifiers do not correspond to study cities, and no study city names, country names, coordinates, city-day records or city-level analytical values are included in this repository.
