"""
build_database.py
Loads data/archangels.json and builds a normalized SQLite warehouse
(data/didacus.db) with tables for archangels, attributes, themes,
sources, prompts and bibliography. This is the single reproducible
step between the raw research dataset and every downstream SQL/pandas
query used in analysis.py and the Streamlit dashboard.
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data" / "archangels.json"
DB_PATH = ROOT / "data" / "didacus.db"

SCHEMA = """
DROP TABLE IF EXISTS archangels;
DROP TABLE IF EXISTS themes;
DROP TABLE IF EXISTS attributes;
DROP TABLE IF EXISTS primary_sources;
DROP TABLE IF EXISTS prompts;
DROP TABLE IF EXISTS confidence;
DROP TABLE IF EXISTS bibliography;
DROP TABLE IF EXISTS archangel_references;

CREATE TABLE archangels (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    name_variants TEXT,
    historical_role TEXT,
    colour_name TEXT,
    colour_status TEXT,
    geometry_metaphor TEXT,
    methodological_caution TEXT
);

CREATE TABLE themes (
    archangel_id INTEGER REFERENCES archangels(id),
    theme TEXT,
    status TEXT CHECK (status IN ('H','R','D'))
);

CREATE TABLE attributes (
    archangel_id INTEGER REFERENCES archangels(id),
    attribute_name TEXT,
    status TEXT CHECK (status IN ('H','R','D')),
    note TEXT
);

CREATE TABLE primary_sources (
    archangel_id INTEGER REFERENCES archangels(id),
    citation TEXT
);

CREATE TABLE prompts (
    archangel_id INTEGER REFERENCES archangels(id),
    prompt TEXT
);

CREATE TABLE confidence (
    archangel_id INTEGER REFERENCES archangels(id),
    dimension TEXT,
    label TEXT,
    score INTEGER
);

CREATE TABLE bibliography (
    key TEXT PRIMARY KEY,
    authors TEXT,
    year INTEGER,
    title TEXT,
    venue TEXT,
    doi TEXT
);

CREATE TABLE archangel_references (
    archangel_id INTEGER REFERENCES archangels(id),
    ref_key TEXT REFERENCES bibliography(key)
);
"""

# Derived scoring convention for confidence labels — created for this
# analysis so qualitative confidence can be charted; not a value stated
# in the source document (see meta.confidence_scale_note in the JSON).
CONFIDENCE_SCORE = {
    "high": 3,
    "high-to-moderate": 2.5,
    "moderate": 2,
    "moderate-to-low": 1.5,
    "low": 1,
    "none documented": 0,
}


def score_for(label: str) -> int:
    return CONFIDENCE_SCORE.get(label.strip().lower(), None)


def build():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    cur = conn.cursor()

    for bib in data["bibliography"]:
        cur.execute(
            "INSERT INTO bibliography (key, authors, year, title, venue, doi) VALUES (?,?,?,?,?,?)",
            (bib["key"], bib["authors"], bib["year"], bib["title"], bib["venue"], bib.get("doi")),
        )

    for a in data["archangels"]:
        cur.execute(
            """INSERT INTO archangels
               (id, name, name_variants, historical_role, colour_name, colour_status,
                geometry_metaphor, methodological_caution)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                a["id"],
                a["name"],
                "; ".join(a["name_variants"]),
                a["historical_role"],
                a["colour"]["name"],
                a["colour"]["status"],
                a["geometry_metaphor"],
                a["methodological_caution"],
            ),
        )

        for theme, status in a["theme_status"].items():
            cur.execute(
                "INSERT INTO themes (archangel_id, theme, status) VALUES (?,?,?)",
                (a["id"], theme, status),
            )

        for attr in a["attributes"]:
            cur.execute(
                "INSERT INTO attributes (archangel_id, attribute_name, status, note) VALUES (?,?,?,?)",
                (a["id"], attr["name"], attr["status"], attr.get("note")),
            )

        for src in a["primary_sources"]:
            cur.execute(
                "INSERT INTO primary_sources (archangel_id, citation) VALUES (?,?)",
                (a["id"], src),
            )

        for prompt in a["contemplative_prompts"]:
            cur.execute(
                "INSERT INTO prompts (archangel_id, prompt) VALUES (?,?)",
                (a["id"], prompt),
            )

        for dimension, label in a["evidence_confidence"].items():
            cur.execute(
                "INSERT INTO confidence (archangel_id, dimension, label, score) VALUES (?,?,?,?)",
                (a["id"], dimension, label, score_for(label)),
            )

        for ref in a.get("references", []):
            cur.execute(
                "INSERT INTO archangel_references (archangel_id, ref_key) VALUES (?,?)",
                (a["id"], ref),
            )

    conn.commit()

    counts = {
        t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ["archangels", "themes", "attributes", "primary_sources", "prompts", "confidence", "bibliography"]
    }
    conn.close()
    return counts


if __name__ == "__main__":
    counts = build()
    print(f"Built {DB_PATH.relative_to(ROOT)}")
    for table, n in counts.items():
        print(f"  {table:16s} {n} rows")
