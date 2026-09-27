"""
analysis.py
Runs SQL queries against data/didacus.db and answers the seven research
questions for the portfolio writeup, saving each supporting chart as a
PNG under outputs/. Run after build_database.py.
"""
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "didacus.db"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

STATUS_LABEL = {"H": "Historical/textual", "R": "Reception-history", "D": "Didacus original"}
# Shared with app/theme.py: gold=historical, teal=reception-history, oxblood=Didacus-original
STATUS_COLOR = {"H": "#C6A25D", "R": "#3E7C74", "D": "#8C2F39"}
plt.rcParams.update({
    "font.family": "serif",
    "axes.edgecolor": "#33384A",
    "axes.titleweight": "medium",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def q(conn, sql, **kw):
    return pd.read_sql_query(sql, conn, **kw)


def main():
    conn = sqlite3.connect(DB_PATH)

    print("=" * 70)
    print("Q1 — Attribute counts per archangel (breadth of visual vocabulary)")
    print("=" * 70)
    df1 = q(conn, """
        SELECT a.name, COUNT(*) AS n_attributes
        FROM attributes attr JOIN archangels a ON a.id = attr.archangel_id
        GROUP BY a.name ORDER BY n_attributes DESC
    """)
    print(df1.to_string(index=False))

    print("\n" + "=" * 70)
    print("Q2 — Most frequently occurring symbols/attributes across all seven")
    print("=" * 70)
    df2 = q(conn, """
        SELECT attribute_name, COUNT(DISTINCT archangel_id) AS n_archangels
        FROM attributes GROUP BY attribute_name
        HAVING n_archangels > 1 ORDER BY n_archangels DESC
    """)
    if df2.empty:
        print("No single named attribute recurs verbatim across archangels —")
        print("each figure's object vocabulary is distinct (see shared attribute *categories* below).")
    else:
        print(df2.to_string(index=False))
    # Cross-cutting categories (colour, scroll/book-type objects, staff-type objects)
    df2b = q(conn, """
        SELECT
          CASE
            WHEN attribute_name LIKE '%book%' OR attribute_name LIKE '%scroll%' THEN 'book/scroll family'
            WHEN attribute_name LIKE '%staff%' OR attribute_name LIKE '%sceptre%' THEN 'staff/sceptre family'
            WHEN attribute_name LIKE '%sword%' THEN 'sword'
            WHEN attribute_name LIKE '%scale%' THEN 'scales'
            ELSE NULL
          END AS symbol_family,
          COUNT(DISTINCT archangel_id) AS n_archangels
        FROM attributes
        WHERE symbol_family IS NOT NULL
        GROUP BY symbol_family ORDER BY n_archangels DESC
    """)
    print("\nCross-cutting symbol families:")
    print(df2b.to_string(index=False))

    print("\n" + "=" * 70)
    print("Q3 — Roles/attributes supported by primary sources (H) vs later tradition (R/D)")
    print("=" * 70)
    df3 = q(conn, "SELECT status, COUNT(*) AS n FROM attributes GROUP BY status ORDER BY n DESC")
    df3["label"] = df3["status"].map(STATUS_LABEL)
    df3["pct"] = (100 * df3["n"] / df3["n"].sum()).round(1)
    print(df3.to_string(index=False))

    print("\n" + "=" * 70)
    print("Q4 — How much of the Didacus system is historically documented vs artist-created?")
    print("=" * 70)
    df4 = q(conn, """
        SELECT a.name,
               SUM(CASE WHEN attr.status='H' THEN 1 ELSE 0 END) AS historical,
               SUM(CASE WHEN attr.status='R' THEN 1 ELSE 0 END) AS reception_history,
               SUM(CASE WHEN attr.status='D' THEN 1 ELSE 0 END) AS didacus_original,
               COUNT(*) AS total
        FROM attributes attr JOIN archangels a ON a.id = attr.archangel_id
        GROUP BY a.name ORDER BY a.name
    """)
    df4["pct_didacus_original"] = (100 * df4["didacus_original"] / df4["total"]).round(0)
    print(df4.to_string(index=False))

    print("\n" + "=" * 70)
    print("Q5 — Colour and geometry per figure (all colours are Didacus-original codes)")
    print("=" * 70)
    df5 = q(conn, "SELECT name, colour_name, colour_status, geometry_metaphor FROM archangels")
    print(df5.to_string(index=False))

    print("\n" + "=" * 70)
    print("Q6 — Symbolic similarity network (archangels sharing symbol families)")
    print("=" * 70)
    print("See outputs/06_symbol_network.png — built with networkx in build_network.py")

    print("\n" + "=" * 70)
    print("Q7 — Evidence-confidence profile: historical vs visual-iconographic strength")
    print("=" * 70)
    df7 = q(conn, """
        SELECT a.name, c.dimension, c.label, c.score
        FROM confidence c JOIN archangels a ON a.id = c.archangel_id
        ORDER BY a.id
    """)
    print(df7.to_string(index=False))

    # ---------------- Charts ----------------

    # Chart 1: attribute count per archangel
    plt.figure(figsize=(8, 4.5))
    plt.bar(df1["name"], df1["n_attributes"], color="#2b6cb0")
    plt.title("Attribute count per archangel")
    plt.ylabel("Number of documented attributes")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(OUT / "01_attribute_counts.png", dpi=150)
    plt.close()

    # Chart 2: H/R/D global split (pie)
    plt.figure(figsize=(5, 5))
    plt.pie(
        df3["n"], labels=df3["label"], autopct="%1.0f%%",
        colors=[STATUS_COLOR[s] for s in df3["status"]],
    )
    plt.title("Attribute provenance across the canon\n(H = historical, R = reception-history, D = Didacus original)")
    plt.tight_layout()
    plt.savefig(OUT / "02_provenance_split.png", dpi=150)
    plt.close()

    # Chart 3: stacked H/R/D per archangel
    pivot = q(conn, """
        SELECT a.name, attr.status, COUNT(*) as n
        FROM attributes attr JOIN archangels a ON a.id = attr.archangel_id
        GROUP BY a.name, attr.status
    """).pivot(index="name", columns="status", values="n").fillna(0)
    pivot = pivot.reindex(columns=["H", "R", "D"], fill_value=0)
    pivot = pivot.loc[[a["name"] for a in
                       sorted(q(conn, "SELECT id,name FROM archangels").to_dict("records"), key=lambda r: r["id"])]]
    ax = pivot.plot(kind="bar", stacked=True,
                     color=[STATUS_COLOR[c] for c in pivot.columns], figsize=(8, 5))
    ax.set_title("Historical vs. reception-history vs. Didacus-original attributes\nby archangel (canonical 1 Enoch 20 order)")
    ax.set_ylabel("Number of attributes")
    ax.legend(title="Status", labels=[STATUS_LABEL[c] for c in pivot.columns])
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(OUT / "03_provenance_by_archangel.png", dpi=150)
    plt.close()

    # Chart 4: evidence confidence heatmap-ish (bar per archangel, mean score)
    df7_valid = df7.dropna(subset=["score"])
    mean_conf = df7_valid.groupby("name")["score"].mean().reindex(
        [a["name"] for a in sorted(q(conn, "SELECT id,name FROM archangels").to_dict("records"), key=lambda r: r["id"])]
    )
    bar_colors = [STATUS_COLOR["H"] if v >= 2.3 else (STATUS_COLOR["R"] if v >= 1.7 else STATUS_COLOR["D"])
                  for v in mean_conf.values]
    plt.figure(figsize=(8, 4.5))
    plt.bar(mean_conf.index, mean_conf.values, color=bar_colors)
    plt.title("Mean evidence-confidence score per archangel\n(derived scale: High=3, Moderate=2, Low=1 — see meta.confidence_scale_note)")
    plt.ylabel("Mean confidence score")
    plt.xticks(rotation=30, ha="right")
    plt.ylim(0, 3)
    plt.tight_layout()
    plt.savefig(OUT / "04_confidence_scores.png", dpi=150)
    plt.close()

    print(f"\nCharts written to {OUT.relative_to(ROOT)}/")
    conn.close()


if __name__ == "__main__":
    main()
