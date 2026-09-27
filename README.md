# Didacus Sacred Neuroart — Data & Visualization Layer

A data-science / BI portfolio project that treats the seven archangels of
*The Seven Archangels* visual atlas as a **structured dataset** rather than
only as artwork — extracted from the companion theoretical framework
(`Didacus Sacred Neuroart: A Theoretical Framework for a Contemporary Canon
of Archangelic Iconography`, v1.0).

The project demonstrates the full pipeline: **research → data modeling →
SQL → pandas analysis → network analysis → interactive dashboard →
storytelling.**

## Why this dataset is interesting

The source paper already does the hard epistemic work: for every attribute
assigned to an archangel, it states whether that attribute is

- **H** — historically / textually attested (present in the primary source),
- **R** — reception-history (a later, established iconographic convention), or
- **D** — a Didacus original invention.

That labelling protocol *is* a clean, analyzable variable. This project
turns it into a queryable dataset and asks: **how much of a "historically
grounded" sacred-art canon is actually historical?**

Headline finding from the current data: across all seven figures, only
**1 of 39** documented attributes (Raphael's fish, from the Book of Tobit)
is directly historically/textually attested. ~41% is later reception-history
iconography, and ~56% is original Didacus artistic invention — with that
split becoming more extreme for the figures with thinner historical
traditions (Raguel, Sariel/Saraqael, Remiel are 75–100% Didacus-original).

## Project structure

```
didacus-project/
├── data/
│   ├── archangels.json      # single source of truth (hand-extracted, cited to the source paper)
│   └── didacus.db           # generated SQLite warehouse (run build_database.py)
├── src/
│   ├── build_database.py    # JSON -> normalized SQLite (archangels, attributes, themes, sources, prompts, confidence, bibliography)
│   ├── analysis.py          # SQL + pandas answers to the 7 research questions, saves charts
│   └── build_network.py     # symbolic similarity network (networkx)
├── app/
│   └── streamlit_app.py     # interactive dashboard, 6 tabs
├── outputs/                 # generated PNG charts
└── requirements.txt
```

## Data model

```
Archangel
 ├── name, name_variants
 ├── didacus_theme[]              (each tagged H/R/D)
 ├── historical_role
 ├── primary_sources[]
 ├── attributes[]                 (each: name, status H/R/D, note)
 ├── colour (name, status)
 ├── geometry_metaphor
 ├── evidence_confidence{}        (per dimension: High/Moderate/Low)
 ├── methodological_caution
 ├── contemplative_prompts[]
 └── references[] -> bibliography
```

## Research questions answered

1. How do the seven archangels differ in their historical attributes? → `analysis.py` Q1/Q4
2. Which symbols occur most frequently? → Q2 (+ cross-cutting "symbol families": staff/sceptre, book/scroll, sword, scales)
3. Which roles are supported by primary sources vs later tradition? → Q3
4. How much of the Didacus system is historically documented vs artist-created? → Q4 (headline finding above)
5. How do colour, geometry and symbolism cluster across the seven figures? → Q5 + dashboard Tab 4
6. Can we construct a symbolic similarity network between archangels? → `build_network.py`, dashboard Tab 3
7. How does historical representation compare with the modern reinterpretation? → Q7, evidence-confidence scores

## Running it

```bash
pip install -r requirements.txt

# 1. Build the SQLite warehouse from the JSON dataset
python src/build_database.py

# 2. Run the SQL/pandas analysis (prints tables, writes charts to outputs/)
python src/analysis.py
python src/build_network.py

# 3. Launch the dashboard
streamlit run app/streamlit_app.py
```

## Dashboard tabs

| Tab | Content |
|---|---|
| 01 Canon Explorer | Interactive per-archangel profile: role, sources, attributes, prompts |
| 02 Historical Evidence | H/R/D provenance breakdown, primary-source citation table |
| 03 Symbol Network | Bipartite archangel↔symbol-family network graph |
| 04 Comparative Matrix | Themes, colour, geometry, % Didacus-original side by side |
| 05 Visual Analytics | Evidence-confidence scores, colour identity per figure |
| 06 Research Layer | Bibliography of the neuroaesthetics/iconography literature behind the framework |

## Notes on scope and honesty of the data

- The dataset is **hand-extracted** from a single source document (the
  theoretical framework), not scraped or independently verified against
  primary texts — this is stated so the project is not misread as a
  systematic-review-grade historical database.
- Numeric confidence scores (0–3 scale) are a **derived convention created
  for this analysis** to make qualitative High/Moderate/Low labels
  chartable; that is documented inline in `data/archangels.json` under
  `meta.confidence_scale_note` and is not a number the source paper states.
- Colour and geometry fields are explicitly Didacus-original canonical
  codes, not historical claims — carried over faithfully from the source
  paper's own framing (colour-emotion associations are "context-dependent
  and vary across cultures").

## Tech stack

Python (pandas, NumPy, matplotlib) · SQLite · NetworkX · Plotly · Streamlit · Git

## Suggested next steps

- Add `pytest` tests for the build/analysis scripts and a GitHub Actions CI workflow (same pattern as the Scientia Caeli repo).
- Deploy the dashboard on Streamlit Community Cloud and link it from the portfolio.
- Write a short IMRaD companion paper framing this as a digital-humanities / cultural-analytics case study.
- Extend the dataset with a second source (e.g. a cross-check against Nickelsburg & VanderKam's 1 Enoch translation) to move some "R"-status attributes toward independently verified "H".
