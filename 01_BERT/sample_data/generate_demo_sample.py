#!/usr/bin/env python3
"""Write the small, fully synthetic public text-classification demonstration."""

from pathlib import Path
import argparse
import json
import pandas as pd

EXAMPLES = [
    ("I felt dizzy and drenched in sweat after a short walk outside.", 1, 7, "positive_physiological"),
    ("My face is flushed and the heat is making me nauseous.", 1, 8, "positive_physiological"),
    ("I am overheated and my head is pounding after waiting outdoors.", 1, 6, "positive_physiological"),
    ("I moved into the shade and kept sipping water until I cooled down.", 1, 7, "positive_coping"),
    ("The fan is on full power but I still cannot get comfortable.", 1, 8, "positive_coping"),
    ("I changed my route so I could avoid the hottest part of the afternoon.", 1, 6, "positive_coping"),
    ("The pavement feels like an oven whenever I step outside.", 1, 7, "positive_ambient_personal"),
    ("The air around me is so hot and still that every errand feels exhausting.", 1, 8, "positive_ambient_personal"),
    ("Even the evening breeze feels warm against my skin tonight.", 1, 9, "positive_ambient_personal"),
    ("This relentless heat is making me irritable and unable to focus.", 1, 7, "positive_psychological"),
    ("I feel trapped indoors and mentally worn down by the hot weather.", 1, 8, "positive_psychological"),
    ("Another sleepless hot night has left me anxious and exhausted.", 1, 9, "positive_psychological"),
    ("The debate became heated after the final question.", 0, 4, "negative_metaphorical"),
    ("That new song is fire and everyone keeps replaying it.", 0, 5, "negative_metaphorical"),
    ("Competition for the award is heating up quickly.", 0, 6, "negative_metaphorical"),
    ("The committee published a revised heat-response policy.", 0, 3, "negative_policy_discourse"),
    ("A public report reviewed national heat-adaptation funding.", 0, 5, "negative_policy_discourse"),
    ("Officials discussed long-term standards for extreme-heat planning.", 0, 10, "negative_policy_discourse"),
    ("Limited offer: save on portable fans while supplies last.", 0, 6, "negative_spam_irrelevant"),
    ("Click here for a guaranteed hot deal on summer accessories.", 0, 7, "negative_spam_irrelevant"),
    ("Automated update: your promotional subscription has been renewed.", 0, 11, "negative_spam_irrelevant"),
    ("The spicy soup arrived steaming hot and tasted wonderful.", 0, 1, "negative_food"),
    ("I added extra chilli because I wanted the dish hotter.", 0, 2, "negative_food"),
    ("Fresh bread is best when it is still warm from the oven.", 0, 12, "negative_food"),
    ("A heat alert was issued, and I felt faint while walking home.", 1, 7, "boundary_positive_alert_personal"),
    ("The warning said to limit activity, which matched how weak I felt outside.", 1, 8, "boundary_positive_alert_personal"),
    ("The agency opened a cooling centre for residents during the alert.", 0, 7, "boundary_negative_institutional_response"),
    ("Emergency services announced extended hours because of the heat.", 0, 8, "boundary_negative_institutional_response"),
    ("The changing climate worries me because I now struggle in hotter afternoons.", 1, 6, "boundary_positive_climate_personal_exposure"),
    ("I can feel summers getting harder on my body each season.", 1, 7, "boundary_positive_climate_personal_exposure"),
    ("My neighbour said the heat made them tired yesterday.", 0, 7, "boundary_negative_third_party"),
    ("A relative complained that the warm night kept them awake.", 0, 8, "boundary_negative_third_party"),
    ("The room stayed hot, and I could not stop sweating at my desk.", 1, 5, "positive_physiological"),
    ("I carried a cold cloth because the outdoor heat felt unbearable.", 1, 9, "positive_coping"),
    ("Hot coffee and toasted sandwiches are today's cafe special.", 0, 2, "negative_commercial_business"),
    ("A retailer announced its summer heating-system maintenance campaign.", 0, 10, "negative_commercial_business"),
]

def build() -> pd.DataFrame:
    return pd.DataFrame([
        {"example_id": f"EX_{i:03d}", "text": text, "label": label, "month": month,
         "example_category": category, "group_id": f"DEMO_G{((i - 1) % 8) + 1:02d}",
         "is_synthetic": True}
        for i, (text, label, month, category) in enumerate(EXAMPLES, start=1)
    ])

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_csv", default=str(Path(__file__).with_name("demo_examples.csv")))
    parser.add_argument("--metadata_json", default=str(Path(__file__).with_name("demo_metadata.json")))
    args = parser.parse_args()
    frame = build()
    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_csv, index=False)
    metadata = {"n_examples": len(frame), "schema": frame.columns.tolist(),
                "label_counts": {str(k): int(v) for k, v in frame.label.value_counts().sort_index().items()},
                "fully_synthetic": True, "scientific_inference": False,
                "note": "Small non-geographic examples for public workflow demonstration only."}
    Path(args.metadata_json).write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    main()
