"""
build_network.py
Constructs a bipartite archangel<->symbol-family graph, then projects it
onto an archangel-archangel similarity network (edge weight = number of
shared symbol families). Answers Q6: "Can we construct a symbolic
similarity network between archangels?"
"""
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "didacus.db"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def symbol_family(attribute_name: str):
    n = attribute_name.lower()
    if "book" in n or "scroll" in n:
        return "book/scroll"
    if "staff" in n or "sceptre" in n:
        return "staff/sceptre"
    if "sword" in n:
        return "sword"
    if "scale" in n:
        return "scales"
    if "star" in n or "celestial" in n or "luminar" in n:
        return "star/celestial"
    if "flame" in n or "fire" in n or "radiant" in n or "orb" in n or "solar" in n or "golden" in n or "gold" in n:
        return "light/fire"
    if "wing" in n:
        return "wings"
    if "vessel" in n or "fish" in n:
        return "water/healing object"
    return None


def main():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT a.name, attr.attribute_name FROM attributes attr JOIN archangels a ON a.id = attr.archangel_id",
        conn,
    )
    conn.close()

    df["family"] = df["attribute_name"].apply(symbol_family)
    df = df.dropna(subset=["family"])

    # Bipartite graph: archangel -- symbol family
    B = nx.Graph()
    archangels = df["name"].unique().tolist()
    families = df["family"].unique().tolist()
    B.add_nodes_from(archangels, bipartite=0)
    B.add_nodes_from(families, bipartite=1)
    for _, row in df.iterrows():
        B.add_edge(row["name"], row["family"])

    # Projection onto archangels: weight = shared symbol families
    G = nx.bipartite.weighted_projected_graph(B, archangels)

    print("Archangel <-> archangel symbolic-similarity edges (shared symbol family count):")
    if G.number_of_edges() == 0:
        print("  No two archangels share a symbol family — each figure's visual vocabulary is distinct.")
    for u, v, data in sorted(G.edges(data=True), key=lambda e: -e[2]["weight"]):
        print(f"  {u} -- {v}: {data['weight']}")

    # Draw the bipartite graph (archangels + symbol families) since that's
    # where the actual shared structure lives, even if the direct
    # archangel-archangel projection is sparse.
    plt.rcParams.update({"font.family": "serif", "figure.facecolor": "white", "axes.facecolor": "white"})
    plt.figure(figsize=(9, 7))
    pos = nx.spring_layout(B, seed=42, k=0.9)
    nx.draw_networkx_nodes(B, pos, nodelist=archangels, node_color="#8C2F39",
                            node_size=1600, label="Archangel")
    nx.draw_networkx_nodes(B, pos, nodelist=families, node_color="#3E7C74",
                            node_size=1000, node_shape="s", label="Symbol family")
    nx.draw_networkx_edges(B, pos, alpha=0.4, edge_color="#33384A")
    nx.draw_networkx_labels(B, pos, font_size=8, font_color="white")
    plt.title("Archangel \u2194 symbol-family network\n(shared object vocabulary across the canon)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(OUT / "06_symbol_network.png", dpi=150)
    plt.close()
    print(f"\nSaved outputs/06_symbol_network.png")


if __name__ == "__main__":
    main()
