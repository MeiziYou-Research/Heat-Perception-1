#!/usr/bin/env python3
"""Generate a deterministic synthetic city-season input for Module 2."""

from pathlib import Path
import numpy as np
import pandas as pd

CONTINENTS = ["Africa", "Asia", "Europe", "North America", "Oceania", "South America"]
SEASONS = ["Spring", "Summer", "Fall", "Winter"]


def main() -> None:
    rng = np.random.default_rng(42)
    rows = []
    city_number = 0
    for continent in CONTINENTS:
        for _ in range(4):
            city_number += 1
            city_id = f"DEMO_UNIT_{city_number:03d}"
            baseline = rng.uniform(0.0006, 0.0040)
            for season_number, season in enumerate(SEASONS):
                rows.append({
                    "city_id": city_id,
                    "continent": continent,
                    "season": season,
                    "HPII": max(0.0, baseline * (0.80 + 0.18 * season_number) + rng.normal(0, 0.0002)),
                    "HPVI": max(0.0, rng.uniform(0.04, 0.42)),
                    "is_synthetic": 1,
                })
    output = Path(__file__).with_name("demo_city_season.csv")
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"Wrote {len(rows)} synthetic city-season records to {output}")


if __name__ == "__main__":
    main()
