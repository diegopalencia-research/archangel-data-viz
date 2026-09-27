"""
Didacus Sacred Neuroart — Data & Visualization dashboard.

Run with:  streamlit run app/streamlit_app.py
Requires:  data/didacus.db (build it first with: python src/build_database.py)
"""
import json
import sqlite3
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from theme import (
    GOLD, TEAL, OXBLOOD, SURFACE, BORDER, TEXT_MUTED,
    STATUS_COLOR, STATUS_LABEL, inject_css, register_template,
)

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "didacus.db"
JSON_PATH = ROOT / "data" / "archangels.json"

# Indicative swatch per canonical colour name — for the colour-identity
# panel only. The Didacus colour system itself is documented (in
# data/archangels.json) as a canonical *coding* system, not a claim
# about one exact pigment; these hexes are a reasonable on-screen
# approximation, not part of the source dataset.
COLOUR_SWATCH = {
    "Deep blue": "#1E3A5F",
    "Green and cream": "#6B8E63",
    "Green/blue": "#2F6B5E",
    "Solar / golden": "#C9A227",
    "Blue-violet": "#5B4B8A",
    "Cool teal": "#2E6E6A",
    "Dawn violet/gold": "#7A5C8A",
}

st.set_page_config(page_title="Didacus — Sacred Neuroart Data Layer", layout="wide")
inject_css(st)
register_template()


@st.cache_data
def load_data():
    if not DB_PATH.exists():
        st.error("Database not found. Run `python src/build_database.py` first.")
        st.stop()
    conn = sqlite3.connect(DB_PATH)
    archangels = pd.read_sql_query("SELECT * FROM archangels ORDER BY id", conn)
    attributes = pd.read_sql_query("SELECT * FROM attributes", conn)
    themes = pd.read_sql_query("SELECT * FROM themes", conn)
    sources = pd.read_sql_query("SELECT * FROM primary_sources", conn)
    prompts = pd.read_sql_query("SELECT * FROM prompts", conn)
    confidence = pd.read_sql_query("SELECT * FROM confidence", conn)
    bibliography = pd.read_sql_query("SELECT * FROM bibliography", conn)
    conn.close()
    raw = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    return archangels, attributes, themes, sources, prompts, confidence, bibliography, raw


archangels, attributes, themes, sources, prompts, confidence, bibliography, raw = load_data()
ORDER = archangels["name"].tolist()

# ---------------------------------------------------------------- Header
st.markdown(
    f"""
    <div class="didacus-header">
        <div class="didacus-eyebrow">DIDACUS SACRED NEUROART</div>
        <div class="didacus-title">Data &amp; Visualization Layer</div>
        <div class="didacus-subtitle">
            The seven archangels of <em>The Seven Archangels</em> atlas, read as a structured
            evidence dataset. Every attribute is coded against the source paper's own
            epistemic protocol — historically attested, reception-history, or Didacus original —
            so the canon's artistic claims stay legible against what the historical record
            actually supports.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- KPI strip
n_archangels = len(archangels)
n_attributes = len(attributes)
pct_h = round(100 * (attributes["status"] == "H").mean())
pct_d = round(100 * (attributes["status"] == "D").mean())
n_refs = len(bibliography)

st.markdown(
    f"""
    <div class="kpi-row">
        <div class="kpi-card"><div class="kpi-value">{n_archangels}</div>
            <div class="kpi-label">Archangels documented</div></div>
        <div class="kpi-card"><div class="kpi-value">{n_attributes}</div>
            <div class="kpi-label">Attributes coded</div></div>
        <div class="kpi-card kpi-accent-h"><div class="kpi-value">{pct_h}%</div>
            <div class="kpi-label">Historically attested</div></div>
        <div class="kpi-card kpi-accent-d"><div class="kpi-value">{pct_d}%</div>
            <div class="kpi-label">Didacus original</div></div>
        <div class="kpi-card"><div class="kpi-value">{n_refs}</div>
            <div class="kpi-label">Literature sources</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Canon", "Evidence", "Network", "Matrix", "Analytics", "Sources"]
)

# ---------------------------------------------------------------- Tab 1 — Canon
with tab1:
    left, right = st.columns([2, 1], gap="large")
    with left:
        name = st.selectbox("Archangel", ORDER, label_visibility="collapsed")
        a = next(x for x in raw["archangels"] if x["name"] == name)

        st.markdown(
            f"""
            <div class="didacus-panel">
                <h4>{a['name']}</h4>
                <div style="color:{TEXT_MUTED}; font-size:0.88rem; margin-bottom:0.8rem;">
                    {', '.join(a['name_variants'])}
                </div>
                <div style="margin-bottom:0.9rem;">{a['historical_role']}</div>
                <div style="color:{TEXT_MUTED}; font-size:0.85rem;">
                    Primary sources: {', '.join(a['primary_sources'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        attr_rows = "".join(
            f"""<div style="margin-bottom:0.55rem;">
                    <span class="status-tag tag-{attr['status']}">{attr['status']}</span>
                    <strong>{attr['name']}</strong>
                    <div style="color:{TEXT_MUTED}; font-size:0.85rem; margin-left:1.6rem;">{attr.get('note','')}</div>
                </div>"""
            for attr in a["attributes"]
        )
        st.markdown(
            f"""<div class="didacus-panel"><h4>Attributes</h4>{attr_rows}
                <div class="didacus-caution"><strong>Methodological caution —</strong> {a['methodological_caution']}</div>
                </div>""",
            unsafe_allow_html=True,
        )

    with right:
        prompts_html = "".join(f"<li style='margin-bottom:0.4rem;'>{p}</li>" for p in a["contemplative_prompts"])
        conf_html = "".join(
            f"<div style='display:flex; justify-content:space-between; margin-bottom:0.4rem; font-size:0.88rem;'>"
            f"<span style='color:{TEXT_MUTED};'>{dim.replace('_',' ')}</span><strong>{label}</strong></div>"
            for dim, label in a["evidence_confidence"].items()
        )
        swatch = COLOUR_SWATCH.get(a["colour"]["name"], "#888888")
        st.markdown(
            f"""
            <div class="didacus-panel">
                <h4>Canonical code</h4>
                <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.6rem;">
                    <span style="width:20px; height:20px; border-radius:2px; background:{swatch}; border:1px solid {BORDER};"></span>
                    <strong>{a['colour']['name']}</strong>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:{TEXT_MUTED};">Geometry</span><strong>{a['geometry_metaphor']}</strong>
                </div>
            </div>
            <div class="didacus-panel"><h4>Evidence confidence</h4>{conf_html}</div>
            <div class="didacus-panel"><h4>Contemplative prompts</h4><ul style="padding-left:1.1rem;">{prompts_html}</ul></div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------- Tab 2 — Evidence
with tab2:
    merged = attributes.merge(archangels[["id", "name"]], left_on="archangel_id", right_on="id")
    merged["status_label"] = merged["status"].map(STATUS_LABEL)

    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        counts = merged.groupby(["name", "status_label"]).size().reset_index(name="count")
        fig = px.bar(
            counts, x="name", y="count", color="status_label",
            color_discrete_map={STATUS_LABEL[k]: v for k, v in STATUS_COLOR.items()},
            category_orders={"name": ORDER, "status_label": [STATUS_LABEL[k] for k in "HRD"]},
            title="Attribute provenance by archangel",
            labels={"name": "", "count": "Attributes", "status_label": ""},
        )
        fig.update_layout(legend=dict(orientation="h", y=-0.18), height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        overall = attributes["status"].value_counts().reindex(["H", "R", "D"]).rename(index=STATUS_LABEL)
        fig2 = go.Figure(go.Pie(
            values=overall.values, labels=overall.index, hole=0.55,
            marker=dict(colors=[STATUS_COLOR[k] for k in "HRD"]),
        ))
        fig2.update_layout(title="Canon-wide split", height=420, showlegend=True,
                            legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        f"""<div class="didacus-panel" style="border-left:2px solid {GOLD};">
        Across all seven figures, only <strong>{(attributes['status']=='H').sum()}</strong> of
        <strong>{len(attributes)}</strong> documented attributes — Raphael's fish, from the Book of
        Tobit — is directly historically/textually attested. The remainder is later reception-history
        iconography or original Didacus invention, a split the source paper states explicitly for
        Raguel, Sariel/Saraqael and Remiel.
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<h4 style='font-family:Spectral;'>Primary-source citations</h4>", unsafe_allow_html=True)
    st.dataframe(
        sources.merge(archangels[["id", "name"]], left_on="archangel_id", right_on="id")[["name", "citation"]]
        .rename(columns={"name": "Archangel", "citation": "Citation"}),
        use_container_width=True, hide_index=True,
    )

# ---------------------------------------------------------------- Tab 3 — Network
with tab3:
    def symbol_family(attribute_name: str):
        n = attribute_name.lower()
        if "book" in n or "scroll" in n: return "book/scroll"
        if "staff" in n or "sceptre" in n: return "staff/sceptre"
        if "sword" in n: return "sword"
        if "scale" in n: return "scales"
        if "star" in n or "celestial" in n or "luminar" in n: return "star/celestial"
        if any(k in n for k in ["flame", "fire", "radiant", "orb", "solar", "gold"]): return "light/fire"
        if "wing" in n: return "wings"
        if "vessel" in n or "fish" in n: return "water/healing object"
        return None

    df = attributes.merge(archangels[["id", "name"]], left_on="archangel_id", right_on="id")
    df["family"] = df["attribute_name"].apply(symbol_family)
    df = df.dropna(subset=["family"])

    B = nx.Graph()
    archs = df["name"].unique().tolist()
    fams = df["family"].unique().tolist()
    B.add_nodes_from(archs, kind="archangel")
    B.add_nodes_from(fams, kind="family")
    for _, row in df.iterrows():
        B.add_edge(row["name"], row["family"])

    pos = nx.spring_layout(B, seed=42, k=0.9)
    edge_x, edge_y = [], []
    for u, v in B.edges():
        edge_x += [pos[u][0], pos[v][0], None]
        edge_y += [pos[u][1], pos[v][1], None]
    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode="lines",
                             line=dict(width=1, color=BORDER), hoverinfo="none")

    node_x, node_y, node_color, node_text, node_size = [], [], [], [], []
    for n_ in B.nodes():
        node_x.append(pos[n_][0]); node_y.append(pos[n_][1])
        is_arch = B.nodes[n_]["kind"] == "archangel"
        node_color.append(OXBLOOD if is_arch else TEAL)
        node_size.append(30 if is_arch else 22)
        node_text.append(n_)
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text", text=node_text, textposition="top center",
        textfont=dict(color="#E9E4D8", size=12),
        marker=dict(size=node_size, color=node_color, line=dict(width=1, color=SURFACE)),
        hoverinfo="text",
    )
    fig3 = go.Figure(data=[edge_trace, node_trace])
    fig3.update_layout(
        showlegend=False, title="Archangel ↔ symbol-family network",
        xaxis=dict(visible=False), yaxis=dict(visible=False), height=560,
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(
        f"""<div style="color:{TEXT_MUTED}; font-size:0.85rem;">
        Oxblood nodes are archangels, teal nodes are shared object families. Two archangels
        joined through the same teal node use overlapping visual vocabulary — Gabriel and
        Sariel/Saraqael, for instance, both carry a scroll-type attribute.</div>""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- Tab 4 — Matrix
with tab4:
    theme_txt = (
        themes.merge(archangels[["id", "name"]], left_on="archangel_id", right_on="id")
        .groupby("name")["theme"].apply(lambda s: " · ".join(s))
    )
    a_join = attributes.merge(archangels[["id", "name"]], left_on="archangel_id", right_on="id")
    matrix = pd.DataFrame({
        "Themes": theme_txt,
        "Colour code": archangels.set_index("name")["colour_name"],
        "Geometry": archangels.set_index("name")["geometry_metaphor"],
        "Attributes": a_join.groupby("name").size(),
        "% Didacus-original": a_join.groupby("name")["status"].apply(lambda s: round(100 * (s == "D").mean())),
    }).reindex(ORDER)
    st.dataframe(
        matrix.style.background_gradient(subset=["% Didacus-original"], cmap="OrRd"),
        use_container_width=True,
    )

# ---------------------------------------------------------------- Tab 5 — Analytics
with tab5:
    conf = confidence.merge(archangels[["id", "name"]], left_on="archangel_id", right_on="id").dropna(subset=["score"])
    mean_conf = conf.groupby("name")["score"].mean().reindex(ORDER)

    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        fig5 = px.bar(
            x=mean_conf.index, y=mean_conf.values,
            labels={"x": "", "y": "Mean confidence (0–3)"},
            title="Mean evidence confidence per archangel",
        )
        fig5.update_traces(
            marker_color=[GOLD if v >= 2.3 else (TEAL if v >= 1.7 else OXBLOOD) for v in mean_conf.values]
        )
        fig5.update_layout(height=420)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown(
            f"""<div style="color:{TEXT_MUTED}; font-size:0.8rem;">
            Score is a derived convention for this dashboard (High=3, Moderate=2, Low=1), not a
            number stated in the source paper — see data/archangels.json → meta.confidence_scale_note.
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        rows = "".join(
            f"""<div style="display:flex; align-items:center; justify-content:space-between; padding:0.5rem 0; border-bottom:1px solid {BORDER};">
                    <span>{row['name']}</span>
                    <span style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="width:14px; height:14px; border-radius:2px; background:{COLOUR_SWATCH.get(row['colour_name'], '#888')}; border:1px solid {BORDER};"></span>
                        <span style="color:{TEXT_MUTED}; font-size:0.85rem;">{row['colour_name']} · {row['geometry_metaphor']}</span>
                    </span>
                </div>"""
            for _, row in archangels.iterrows()
        )
        st.markdown(f"""<div class="didacus-panel"><h4>Colour identity across the canon</h4>{rows}</div>""",
                     unsafe_allow_html=True)

# ---------------------------------------------------------------- Tab 6 — Sources
with tab6:
    st.markdown("<h4 style='font-family:Spectral;'>Research layer</h4>", unsafe_allow_html=True)
    st.dataframe(
        bibliography[["authors", "year", "title", "venue", "doi"]]
        .sort_values("year")
        .rename(columns={"authors": "Authors", "year": "Year", "title": "Title", "venue": "Venue", "doi": "DOI"}),
        use_container_width=True, hide_index=True,
    )
    st.markdown(
        f"""<div style="color:{TEXT_MUTED}; font-size:0.85rem; margin-top:0.8rem;">
        The neuroaesthetics, symmetry-perception, colour-emotion, Byzantine-iconography and
        Enochic scholarship the theoretical framework synthesises — the layer that separates
        Didacus's artistic claims from established findings.</div>""",
        unsafe_allow_html=True,
    )
