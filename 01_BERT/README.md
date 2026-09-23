# Heat-perception text-classification workflow

This module contains the shared code for candidate retrieval, rule filtering, deduplication and account-hygiene checks, labelled-data preparation, BERT fine-tuning, evaluation and audit export.

The original X/Twitter corpus and labelled source text are not included or offered for redistribution. The repository includes a small set of fully synthetic examples selected to illustrate the shared text-classification workflow. These examples do not reproduce the study sample, geographic distribution, training corpus or validation corpus and are not intended for scientific inference.

`sample_data/demo_examples.csv` contains 36 artificial examples. It contains no tweet identifiers, usernames, URLs, dates, years, locations or real geographic identifiers. `group_id` is a purely synthetic grouping variable used only to exercise grouped cross-validation; it does not correspond to a city.

The final validation figure is Supplementary Figure S22. Numerical validation results should be taken from the final manuscript and Supplementary Information rather than inferred from the synthetic demonstration.

Training and validation use a maximum BERT input length of 512 tokens. Sequences are truncated only when they exceed this limit.

## Demonstration order

Regenerate the demonstration file with `python sample_data/generate_demo_sample.py`. The public demo defaults to `text`, `label`, integer `month` and `group_id`. Production inputs may use different column names through the scripts' command-line options. Model training downloads the specified pretrained model and is therefore not an offline or lightweight check. Index construction is maintained separately in `../02_indices/` and does not require geographic fields to be added to the BERT demonstration.

## Minimum input schema

The preferred demonstration schema is `example_id,text,label,month,example_category,group_id,is_synthetic`.

Nature Communications Source Data are prepared and distributed separately. The synthetic examples are not manuscript Source Data.

## Environment

The recorded environment uses Python 3.9.24, pandas 2.0.3, NumPy 1.21.6, scikit-learn 1.5.0, PyTorch 2.2.1, Transformers 4.38.1 and NLTK 3.7. Install the exact package versions listed in `requirements.txt`.
