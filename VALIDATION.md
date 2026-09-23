# Validation

## Public text demonstration

The Module 1 public demonstration contains 36 fully synthetic, non-geographic examples with the schema `example_id,text,label,month,example_category,group_id,is_synthetic`. Static checks confirm integer months 1–12, unique example identifiers, eight synthetic groups and balanced binary labels. Scripts 01–04 execute on this schema without requiring city, country, continent, coordinates, exact dates or a preassigned split.

The Module 2 execution example contains only synthetic `DEMO_UNIT_*` identifiers and synthetic index values. It contains no study city names, country names, coordinates, city-day records or city-level analytical values.

The demonstration is a code-path check only. It is not used to validate manuscript performance estimates, reproduce Supplementary Figure S22 or generate Nature Communications Source Data.

## Successfully validated

- Python source files passed syntax parsing.
- Synthetic Module 1 preprocessing steps 01–04 completed using the 36-example, non-geographic demonstration schema.
- The public Module 2 demonstration was checked only as a synthetic code-path example. The 48 study HPPI values released for the article are limited to the rows and columns in the `Fig. 6` sheet of `Source Data.xlsx`.
- Main-text Figure 7 and Figure 8 scripts read only their named formal Source Data sheets and produced vector-only PDF test outputs with zero raster image objects.
- Shared code was checked for absolute local filesystem paths and obsolete methodological terminology.

## Scope limitations

- BERT fitting and manuscript performance estimates were not rerun from the restricted labelled text.
- Restricted health models were not re-executed because the authorized city-day health data are not publicly distributed.
- Syntax parsing of the shared R scripts is reported separately below and does not imply execution of the restricted models.

## Public-data limitations

The public synthetic material demonstrates software behavior and expected schemas. It is not derived from real posts and is not intended for scientific inference. Restricted source datasets and the article Source Data workbook are not included in this repository.

## R syntax status

Both shared full-study-period R scripts passed `parse()` using R 4.3.3. Required packages are declared in the module README and are either loaded explicitly or called with explicit namespaces. This syntax check does not constitute re-execution of the restricted health models.
