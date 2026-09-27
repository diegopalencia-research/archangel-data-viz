"""
theme.py — shared design tokens for the Didacus dashboard.

One palette, one type system, one Plotly template, imported everywhere
so the interactive dashboard, the static analysis charts and the README
all read as one visual system.
"""
import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------- Tokens
INK = "#12141C"          # page background
SURFACE = "#1B1E29"      # panel background
SURFACE_2 = "#232733"    # slightly raised panel
BORDER = "#2E3242"       # hairline rule
TEXT = "#E9E4D8"         # parchment — primary text
TEXT_MUTED = "#9A9CAE"   # secondary text

GOLD = "#C6A25D"      # H — historically / textually attested
TEAL = "#3E7C74"      # R — reception-history / later convention
OXBLOOD = "#8C2F39"   # D — Didacus original invention

STATUS_COLOR = {"H": GOLD, "R": TEAL, "D": OXBLOOD}
STATUS_LABEL = {"H": "Historically attested", "R": "Reception-history", "D": "Didacus original"}

FONT_DISPLAY = "Spectral, Georgia, serif"
FONT_UI = "Inter, -apple-system, sans-serif"


def inject_css(st):
    """Call once near the top of the app. Loads fonts, restyles Streamlit
    chrome (tabs, metrics, dataframes) to match the manuscript/analyst
    palette instead of default Streamlit styling."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: {FONT_UI};
        }}

        .stApp {{
            background-color: {INK};
        }}

        /* Header band */
        .didacus-header {{
            border-bottom: 1px solid {BORDER};
            padding-bottom: 1.1rem;
            margin-bottom: 1.4rem;
        }}
        .didacus-eyebrow {{
            font-family: {FONT_UI};
            font-size: 0.78rem;
            color: {GOLD};
            letter-spacing: 0.02em;
            margin-bottom: 0.15rem;
        }}
        .didacus-title {{
            font-family: {FONT_DISPLAY};
            font-size: 2.1rem;
            font-weight: 600;
            color: {TEXT};
            margin: 0;
        }}
        .didacus-subtitle {{
            font-family: {FONT_UI};
            font-size: 0.95rem;
            color: {TEXT_MUTED};
            max-width: 62ch;
            line-height: 1.55;
            margin-top: 0.5rem;
        }}

        /* KPI strip */
        .kpi-row {{ display: flex; gap: 1px; background: {BORDER};
                     border: 1px solid {BORDER}; margin-bottom: 1.6rem; }}
        .kpi-card {{ flex: 1; background: {SURFACE}; padding: 1rem 1.2rem; }}
        .kpi-value {{ font-family: {FONT_DISPLAY}; font-size: 1.9rem;
                       font-weight: 600; color: {TEXT}; line-height: 1; }}
        .kpi-label {{ font-family: {FONT_UI}; font-size: 0.78rem;
                       color: {TEXT_MUTED}; margin-top: 0.35rem; }}
        .kpi-accent-h .kpi-value {{ color: {GOLD}; }}
        .kpi-accent-r .kpi-value {{ color: {TEAL}; }}
        .kpi-accent-d .kpi-value {{ color: {OXBLOOD}; }}

        /* Panel */
        .didacus-panel {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
        }}
        .didacus-panel h4 {{
            font-family: {FONT_DISPLAY}; color: {TEXT};
            font-size: 1.15rem; margin-top: 0; margin-bottom: 0.6rem;
        }}
        .status-tag {{
            display: inline-block; font-size: 0.72rem; font-family: {FONT_UI};
            padding: 0.05rem 0.45rem; border-radius: 2px; margin-right: 0.4rem;
            color: {INK}; font-weight: 600;
        }}
        .tag-H {{ background: {GOLD}; }}
        .tag-R {{ background: {TEAL}; }}
        .tag-D {{ background: {OXBLOOD}; }}

        .didacus-caution {{
            border-left: 2px solid {OXBLOOD};
            padding: 0.6rem 0.9rem;
            background: {SURFACE_2};
            color: {TEXT_MUTED};
            font-size: 0.88rem;
            margin-top: 0.8rem;
        }}

        /* Tabs: underline indicator instead of default pill buttons */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 1.6rem;
            border-bottom: 1px solid {BORDER};
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: {FONT_UI};
            font-size: 0.92rem;
            color: {TEXT_MUTED};
            background: transparent;
            padding: 0.5rem 0.1rem;
        }}
        .stTabs [aria-selected="true"] {{
            color: {TEXT} !important;
            border-bottom: 2px solid {GOLD};
        }}

        /* Dataframes */
        [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; }}

        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def plotly_template() -> go.layout.Template:
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor=SURFACE,
            plot_bgcolor=SURFACE,
            font=dict(family=FONT_UI, color=TEXT, size=13),
            title=dict(font=dict(family=FONT_DISPLAY, size=17, color=TEXT)),
            colorway=[GOLD, TEAL, OXBLOOD, "#5C6178", "#7C8A9E"],
            xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
            yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=56, l=48, r=24, b=48),
        )
    )


def register_template():
    pio.templates["didacus"] = plotly_template()
    pio.templates.default = "didacus"
