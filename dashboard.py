import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Brent Expiry Fly Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Contract metadata ─────────────────────────────────────────────────────────
ORDER = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}
CONTRACT_META = {
    "F": {"delivery": 1,  "last_traded": 11, "label": "F (Jan)"},
    "G": {"delivery": 2,  "last_traded": 12, "label": "G (Feb)"},
    "H": {"delivery": 3,  "last_traded": 1,  "label": "H (Mar)"},
    "J": {"delivery": 4,  "last_traded": 2,  "label": "J (Apr)"},
    "K": {"delivery": 5,  "last_traded": 3,  "label": "K (May)"},
    "M": {"delivery": 6,  "last_traded": 4,  "label": "M (Jun)"},
    "N": {"delivery": 7,  "last_traded": 5,  "label": "N (Jul)"},
    "Q": {"delivery": 8,  "last_traded": 6,  "label": "Q (Aug)"},
    "U": {"delivery": 9,  "last_traded": 7,  "label": "U (Sep)"},
    "V": {"delivery": 10, "last_traded": 8,  "label": "V (Oct)"},
    "X": {"delivery": 11, "last_traded": 9,  "label": "X (Nov)"},
    "Z": {"delivery": 12, "last_traded": 10, "label": "Z (Dec)"},
}
TYPICAL_DIR = {
    "F": ("LEAN_LONG", 7, 10),
    "G": ("MIXED", 5, 10),
    "H": ("STRONG_LONG", 8, 10),
    "J": ("SLIGHT_LONG", 6, 11),
    "K": ("LEAN_LONG", 7, 11),
    "M": ("STRONG_LONG", 8, 11),
    "N": ("STRONG_SHORT", 2, 11),
    "Q": ("STRONG_LONG", 9, 10),
    "U": ("LEAN_LONG", 7, 10),
    "V": ("SLIGHT_LONG", 6, 10),
    "X": ("SLIGHT_LONG", 6, 10),
    "Z": ("SLIGHT_SHORT", 4, 10),
}

def prev_letters(letter):
    i = ORDER.index(letter)
    p1 = ORDER[(i - 1) % len(ORDER)]
    p2 = ORDER[(i - 2) % len(ORDER)]
    return p1, p2

def prev_year(letter, prev_letter, year):
    i_curr = ORDER.index(letter)
    i_prev = ORDER.index(prev_letter)
    return year - 1 if i_prev > i_curr else year

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    lc  = pd.read_csv("data/analysis/all_contracts_lifecycle.csv", parse_dates=["date"])
    tbl = pd.read_csv("data/analysis/all12_contract_tables.csv")
    bot = pd.read_csv("data/bot/bot_bfoe_daily.csv", parse_dates=["date"])
    bft = pd.read_csv("data/analysis/all12_bot_features.csv")
    bic = pd.read_csv("data/analysis/all12_bot_ic.csv")
    return lc, tbl, bot, bft, bic

lc, tbl, bot, bft, bic = load_data()
bot_idx = bot.set_index("date")

# ── Theme toggle ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Brent Expiry Fly")
    theme = st.radio("Theme", ["Dark", "Light"], index=0, horizontal=True)
    st.markdown("---")
    contract_letter = st.selectbox(
        "Select Contract",
        ORDER,
        index=ORDER.index("M"),
        format_func=lambda x: CONTRACT_META[x]["label"],
    )
    st.markdown("---")
    avail_years = sorted(
        tbl[tbl["contract_letter"] == contract_letter]["year"].unique(), reverse=True
    )
    selected_year = st.selectbox("Year (for lifecycle chart)", avail_years, index=0)
    st.markdown("---")
    st.markdown("**Entry:** td7 → **Exit:** DTE3")
    td_label, wins, total = TYPICAL_DIR[contract_letter]
    col1, col2 = st.columns(2)
    col1.metric("Typical Direction", td_label.replace("_", " "))
    col2.metric("Win Rate", f"{wins}/{total} ({int(wins/total*100)}%)")

# ── Theme colors ──────────────────────────────────────────────────────────────
if theme == "Dark":
    BG = "#0e1117"
    PAPER = "#1a1d27"
    CARD = "#1e2130"
    BORDER = "#2d3250"
    TEXT = "#e0e0e0"
    SUBTEXT = "#888"
    GRID = "#2a2d3e"
    PLOT_TEMPLATE = "plotly_dark"
    TABLE_HEADER_BG = "#2d3250"
    TABLE_CELL_BG = "#1a1d27"
    TABLE_ALT_BG = "#1e2130"
    TABLE_FONT = "#e0e0e0"
    LONG_COLOR = "#00d97e"
    SHORT_COLOR = "#f85149"
    WARN_COLOR = "#f0883e"
    NEUTRAL_COLOR = "#888"
    CONFIRM_COLOR = "#388bfd"
else:
    BG = "#f8f9fa"
    PAPER = "#ffffff"
    CARD = "#f0f2f5"
    BORDER = "#d0d7de"
    TEXT = "#1c1e24"
    SUBTEXT = "#555"
    GRID = "#e0e0e0"
    PLOT_TEMPLATE = "plotly_white"
    TABLE_HEADER_BG = "#e6eaf0"
    TABLE_CELL_BG = "#ffffff"
    TABLE_ALT_BG = "#f4f6fa"
    TABLE_FONT = "#1c1e24"
    LONG_COLOR = "#1a7f45"
    SHORT_COLOR = "#cf2424"
    WARN_COLOR = "#d97706"
    NEUTRAL_COLOR = "#555"
    CONFIRM_COLOR = "#1a56db"

st.markdown(f"""
<style>
    .stApp {{ background-color: {BG}; }}
    .block-container {{ padding: 1.2rem 1.5rem; }}
    .metric-card {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px;
        padding: 14px 18px; margin-bottom: 10px;
    }}
    .metric-label {{ font-size: 11px; color: {SUBTEXT}; text-transform: uppercase; letter-spacing: 0.05em; }}
    .metric-value {{ font-size: 22px; font-weight: 700; color: {TEXT}; margin-top: 2px; }}
    .section-header {{
        font-size: 13px; font-weight: 600; color: {SUBTEXT};
        text-transform: uppercase; letter-spacing: 0.08em;
        border-bottom: 1px solid {BORDER}; padding-bottom: 6px; margin-bottom: 12px;
    }}
    .tag-long {{ background: {LONG_COLOR}22; color: {LONG_COLOR}; padding: 2px 8px;
                border-radius: 4px; font-size: 12px; font-weight: 600; }}
    .tag-short {{ background: {SHORT_COLOR}22; color: {SHORT_COLOR}; padding: 2px 8px;
                 border-radius: 4px; font-size: 12px; font-weight: 600; }}
    .tag-mixed {{ background: {NEUTRAL_COLOR}22; color: {NEUTRAL_COLOR}; padding: 2px 8px;
                 border-radius: 4px; font-size: 12px; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
p1_letter, p2_letter = prev_letters(contract_letter)
st.markdown(
    f"<h2 style='color:{TEXT}; margin-bottom:4px;'>"
    f"CO{contract_letter} — {CONTRACT_META[contract_letter]['label']} Fly</h2>"
    f"<p style='color:{SUBTEXT}; margin-top:0; font-size:13px;'>"
    f"prev-1: CO{p1_letter} &nbsp;|&nbsp; prev-2: CO{p2_letter} &nbsp;|&nbsp; "
    f"Fly = CO_front − 2×CO_center + CO_back &nbsp;|&nbsp; Entry td7 → Exit DTE3</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: LIFECYCLE CHART — selected year, 3 months observation window
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-header'>Lifecycle Chart — CO{contract_letter}{str(selected_year)[-2:]} with CO{p1_letter} & CO{p2_letter} (3-month window)</div>", unsafe_allow_html=True)

def get_lifecycle(letter, year, slot=None):
    mask = lc["contract"] == f"CO{letter}{str(year)[-2:]}"
    sub = lc[mask].copy()
    if slot is not None:
        sub = sub[sub["co_slot"] == slot]
    return sub.sort_values("date")

# Main contract: all 3 slots (full 3-month window)
main_all = get_lifecycle(contract_letter, selected_year)

# Prev-1 and prev-2: only co_slot=1 (their own expiry month)
p1_yr = prev_year(contract_letter, p1_letter, selected_year)
p2_yr = prev_year(contract_letter, p2_letter, selected_year)
prev1_data = get_lifecycle(p1_letter, p1_yr, slot=1)
prev2_data = get_lifecycle(p2_letter, p2_yr, slot=1)

fig = make_subplots(
    rows=1, cols=1,
    subplot_titles=[
        f"CO{contract_letter}{str(selected_year)[-2:]} — Fly Price (3-month window: CO3 → CO2 → CO1 slot)",
    ],
)

SLOT_COLORS = {3: "#7b8cde", 2: "#50c8af", 1: "#f4a44a"}
SLOT_LABELS = {3: "CO3 slot (3 months out)", 2: "CO2 slot (2 months out)", 1: "CO1 slot (expiry month)"}

# Plot each slot separately so color changes at month boundary
for slot in [3, 2, 1]:
    sd = main_all[main_all["co_slot"] == slot]
    if sd.empty:
        continue
    fig.add_trace(go.Scatter(
        x=sd["date"], y=sd["fly"],
        mode="lines", name=SLOT_LABELS[slot],
        line=dict(color=SLOT_COLORS[slot], width=2),
        hovertemplate="<b>%{x|%b %d}</b><br>Fly: %{y:.3f}<extra>" + SLOT_LABELS[slot] + "</extra>",
    ))

# Entry td7 marker and exit DTE3 marker on main contract slot 1
slot1 = main_all[main_all["co_slot"] == 1]
entry_row = slot1[slot1["td_in_month"] == 7]
exit_row = slot1[slot1["td_to_expiry"].round() == 3]
if not entry_row.empty:
    fig.add_trace(go.Scatter(
        x=entry_row["date"], y=entry_row["fly"],
        mode="markers", name="Entry (td7)",
        marker=dict(symbol="triangle-up", size=14, color=LONG_COLOR,
                    line=dict(width=1.5, color=TEXT)),
        showlegend=True,
    ))
if not exit_row.empty:
    fig.add_trace(go.Scatter(
        x=exit_row["date"], y=exit_row["fly"],
        mode="markers", name="Exit (DTE3)",
        marker=dict(symbol="triangle-down", size=14, color=SHORT_COLOR,
                    line=dict(width=1.5, color=TEXT)),
        showlegend=True,
    ))

# Overlay prev-1 and prev-2 fly lines (dashed, lighter)
if not prev1_data.empty:
    fig.add_trace(go.Scatter(
        x=prev1_data["date"], y=prev1_data["fly"],
        mode="lines", name=f"CO{p1_letter}{str(p1_yr)[-2:]} (prev-1)",
        line=dict(color="#9b59b6", width=1.5, dash="dot"),
        hovertemplate="<b>%{x|%b %d}</b><br>prev-1 Fly: %{y:.3f}<extra></extra>",
    ))
if not prev2_data.empty:
    fig.add_trace(go.Scatter(
        x=prev2_data["date"], y=prev2_data["fly"],
        mode="lines", name=f"CO{p2_letter}{str(p2_yr)[-2:]} (prev-2)",
        line=dict(color="#e67e22", width=1.5, dash="dot"),
        hovertemplate="<b>%{x|%b %d}</b><br>prev-2 Fly: %{y:.3f}<extra></extra>",
    ))

fig.update_layout(
    template=PLOT_TEMPLATE,
    paper_bgcolor=PAPER,
    plot_bgcolor=PAPER,
    height=380,
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        orientation="h", y=1.08, x=0,
        bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT),
    ),
    font=dict(color=TEXT),
    hovermode="x unified",
)
fig.update_xaxes(showgrid=True, gridcolor=GRID, tickfont=dict(size=10, color=SUBTEXT))
fig.update_yaxes(showgrid=True, gridcolor=GRID, tickfont=dict(size=10, color=SUBTEXT))

st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# COMPARISON CHART: Fly / CO1-CO2 Backw / OI  ×  current + prev-1 + prev-2
# X-axis: DTE (trading days to expiry) — aligns all 3 contracts on same scale
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<div class='section-header'>"
    f"Fly · Backwardation · OI Comparison — "
    f"CO{contract_letter}{str(selected_year)[-2:]} vs CO{p1_letter}{str(p1_yr)[-2:]} (prev-1) vs CO{p2_letter}{str(p2_yr)[-2:]} (prev-2)"
    f"</div>",
    unsafe_allow_html=True,
)

# Build DTE-aligned data for current, prev-1, prev-2 (CO1 slot only)
def dte_series(letter, year):
    sub = lc[(lc["contract"] == f"CO{letter}{str(year)[-2:]}") & (lc["co_slot"] == 1)].copy()
    sub = sub[sub["td_to_expiry"].notna()].sort_values("td_to_expiry", ascending=False)
    return sub

def entry_dte_for(df):
    """Return the DTE value at td_in_month==7 (actual entry day)."""
    row = df[df["td_in_month"] == 7]
    if row.empty:
        return None
    return float(row["td_to_expiry"].iloc[0])

curr_dte  = dte_series(contract_letter, selected_year)
prev1_dte = dte_series(p1_letter, p1_yr)
prev2_dte = dte_series(p2_letter, p2_yr)

# Compute actual entry DTE for each contract (td_in_month==7 → its DTE)
curr_entry_dte  = entry_dte_for(curr_dte)
prev1_entry_dte = entry_dte_for(prev1_dte)
prev2_entry_dte = entry_dte_for(prev2_dte)

CURR_COLOR  = "#f4a44a"   # orange — current contract
PREV1_COLOR = "#9b59b6"   # purple — prev-1
PREV2_COLOR = "#e67e22"   # amber  — prev-2

fig_comp = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    subplot_titles=[
        "Fly Price (CO1 slot)",
        "CO1-CO2 Backwardation",
        "Open Interest (thousands)",
        "BOT: bid_imbal (3-day avg)  &  moc_net_bid (3-day avg)",
    ],
    vertical_spacing=0.05,
    row_heights=[0.32, 0.22, 0.22, 0.24],
)

# ── Build rolling-3-day BOT series aligned to DTE for a single contract ──────
def bot_dte_series(df_lc):
    """
    For each row in the CO1 lifecycle df, look up 3-day centred BOT average.
    Returns a df with td_to_expiry, bid_imbal_3d, moc_net_bid_3d columns.
    """
    rows = []
    for _, r in df_lc[df_lc["td_to_expiry"].notna()].iterrows():
        d = r["date"]
        window = bot_idx[
            (bot_idx.index >= d - pd.Timedelta("4d")) &
            (bot_idx.index <= d + pd.Timedelta("4d"))
        ].copy()
        if window.empty:
            rows.append({"td_to_expiry": r["td_to_expiry"],
                         "bid_imbal_3d": np.nan, "moc_net_bid_3d": np.nan})
            continue
        window = window.iloc[(window.index - d).to_series().abs().argsort()[:3]]
        rows.append({
            "td_to_expiry":  r["td_to_expiry"],
            "bid_imbal_3d":  window["bid_imbal"].mean(),
            "moc_net_bid_3d": window["moc_net_bid"].mean(),
        })
    return pd.DataFrame(rows).sort_values("td_to_expiry", ascending=False)

# ── helper: add all 4 panels for one contract ─────────────────────────────────
def add_comp_series(df, label, color, entry_dte, is_main=False):
    lw   = 2.2 if is_main else 1.4
    dash = "solid" if is_main else "dot"

    def entry_marker(panel_df, y_col, row_n):
        if entry_dte is None: return
        nearest = panel_df.iloc[(panel_df["td_to_expiry"] - entry_dte).abs().argsort()[:1]]
        if nearest.empty: return
        fig_comp.add_trace(go.Scatter(
            x=nearest["td_to_expiry"], y=nearest[y_col],
            mode="markers", name=f"{label} entry",
            marker=dict(symbol="circle", size=10, color=color,
                        line=dict(width=2, color=TEXT)),
            legendgroup=label, showlegend=False,
            hovertemplate=f"<b>Entry td7</b> DTE %{{x:.0f}} %{{y:.3f}}<extra>{label}</extra>",
        ), row=row_n, col=1)

    # Row 1 — Fly
    fly_d = df[df["fly"].notna()].copy()
    if not fly_d.empty:
        fig_comp.add_trace(go.Scatter(
            x=fly_d["td_to_expiry"], y=fly_d["fly"],
            mode="lines", name=label,
            line=dict(color=color, width=lw, dash=dash),
            legendgroup=label, showlegend=True,
            hovertemplate=f"<b>{label}</b> DTE %{{x:.0f}} fly=%{{y:.3f}}<extra></extra>",
        ), row=1, col=1)
        entry_marker(fly_d, "fly", 1)

    # Row 2 — Backwardation
    bw_d = df[df["backw"].notna()].copy()
    if not bw_d.empty:
        fig_comp.add_trace(go.Scatter(
            x=bw_d["td_to_expiry"], y=bw_d["backw"],
            mode="lines", name=label,
            line=dict(color=color, width=lw, dash=dash),
            legendgroup=label, showlegend=False,
            hovertemplate=f"<b>{label}</b> DTE %{{x:.0f}} backw=%{{y:.3f}}<extra></extra>",
        ), row=2, col=1)
        entry_marker(bw_d, "backw", 2)

    # Row 3 — OI: bars for current, lines for prev
    oi_d = df[df["oi"].notna()].copy()
    if not oi_d.empty:
        if is_main:
            fig_comp.add_trace(go.Bar(
                x=oi_d["td_to_expiry"], y=oi_d["oi"] / 1000,
                name=label, marker_color=color, opacity=0.75,
                legendgroup=label, showlegend=False,
                hovertemplate=f"<b>{label}</b> DTE %{{x:.0f}} OI=%{{y:,.0f}}k<extra></extra>",
            ), row=3, col=1)
        else:
            fig_comp.add_trace(go.Scatter(
                x=oi_d["td_to_expiry"], y=oi_d["oi"] / 1000,
                mode="lines", name=label,
                line=dict(color=color, width=1.4, dash="dot"),
                legendgroup=label, showlegend=False,
                hovertemplate=f"<b>{label}</b> DTE %{{x:.0f}} OI=%{{y:,.0f}}k<extra></extra>",
            ), row=3, col=1)

    # Row 4 — BOT 3-day rolling: bid_imbal (left axis) + moc_net_bid (right axis)
    bot_d = bot_dte_series(df)
    bi_d  = bot_d[bot_d["bid_imbal_3d"].notna()]
    mn_d  = bot_d[bot_d["moc_net_bid_3d"].notna()]
    if not bi_d.empty:
        fig_comp.add_trace(go.Scatter(
            x=bi_d["td_to_expiry"], y=bi_d["bid_imbal_3d"],
            mode="lines", name=f"{label} bid_imbal",
            line=dict(color=color, width=lw, dash=dash),
            legendgroup=label, showlegend=False,
            hovertemplate=f"<b>{label}</b> DTE %{{x:.0f}} bid_imbal=%{{y:.3f}}<extra></extra>",
        ), row=4, col=1)
    if not mn_d.empty:
        fig_comp.add_trace(go.Bar(
            x=mn_d["td_to_expiry"], y=mn_d["moc_net_bid_3d"],
            name=f"{label} moc_net",
            marker_color=color, opacity=0.35,
            legendgroup=label, showlegend=False,
            hovertemplate=f"<b>{label}</b> DTE %{{x:.0f}} moc_net=%{{y:.0f}}<extra></extra>",
        ), row=4, col=1)

add_comp_series(curr_dte,  f"CO{contract_letter}{str(selected_year)[-2:]} (current)",
                CURR_COLOR,  curr_entry_dte,  is_main=True)
if not prev1_dte.empty:
    add_comp_series(prev1_dte, f"CO{p1_letter}{str(p1_yr)[-2:]} (prev-1)",
                    PREV1_COLOR, prev1_entry_dte, is_main=False)
if not prev2_dte.empty:
    add_comp_series(prev2_dte, f"CO{p2_letter}{str(p2_yr)[-2:]} (prev-2)",
                    PREV2_COLOR, prev2_entry_dte, is_main=False)

# ── Reference lines ───────────────────────────────────────────────────────────
fig_comp.add_hline(y=0,    line=dict(color=GRID,        width=1,   dash="dash"), row=2, col=1)
fig_comp.add_hline(y=0.5,  line=dict(color=LONG_COLOR,  width=0.8, dash="dot"),  row=2, col=1)
fig_comp.add_hline(y=-0.5, line=dict(color=SHORT_COLOR, width=0.8, dash="dot"),  row=2, col=1)
fig_comp.add_hline(y=1.0,  line=dict(color=LONG_COLOR,  width=0.8, dash="dot"),  row=4, col=1)
fig_comp.add_hline(y=0,    line=dict(color=GRID,        width=1,   dash="dash"), row=4, col=1)

# ── Entry vlines per contract ─────────────────────────────────────────────────
for entry_x, vcolor, label_str in [
    (curr_entry_dte,  CURR_COLOR,  f"td7 ({contract_letter}{str(selected_year)[-2:]})"),
    (prev1_entry_dte, PREV1_COLOR, f"td7 ({p1_letter}{str(p1_yr)[-2:]})"),
    (prev2_entry_dte, PREV2_COLOR, f"td7 ({p2_letter}{str(p2_yr)[-2:]})"),
]:
    if entry_x is None:
        continue
    for row_n in [1, 2, 3, 4]:
        fig_comp.add_vline(
            x=entry_x,
            line=dict(color=vcolor, width=1.0, dash="dash"),
            annotation_text=label_str if row_n == 1 else "",
            annotation_font=dict(color=vcolor, size=9),
            row=row_n, col=1,
        )

# ── Exit vline ────────────────────────────────────────────────────────────────
for row_n in [1, 2, 3, 4]:
    fig_comp.add_vline(
        x=3,
        line=dict(color=SHORT_COLOR, width=1.4, dash="dash"),
        annotation_text="Exit DTE3" if row_n == 1 else "",
        annotation_font=dict(color=SHORT_COLOR, size=10),
        row=row_n, col=1,
    )

fig_comp.update_layout(
    template=PLOT_TEMPLATE,
    paper_bgcolor=PAPER,
    plot_bgcolor=PAPER,
    height=900,
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        orientation="h", y=1.03, x=0,
        bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT),
    ),
    font=dict(color=TEXT),
    hovermode="x unified",
    bargap=0.05,
)
for row_n in [1, 2, 3, 4]:
    fig_comp.update_xaxes(
        autorange="reversed",
        showgrid=True, gridcolor=GRID,
        tickfont=dict(size=10, color=SUBTEXT),
        title_text="Trading Days to Expiry (DTE) →" if row_n == 4 else "",
        row=row_n, col=1,
    )
fig_comp.update_yaxes(showgrid=True, gridcolor=GRID, tickfont=dict(size=10, color=SUBTEXT))

st.plotly_chart(fig_comp, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: ALL-YEARS LIFECYCLE — small multiples overlay chart
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-header'>All-Years Overlay — CO{contract_letter} Fly (CO1 slot, expiry month only)</div>", unsafe_allow_html=True)

all_years_data = lc[(lc["contract"].str.startswith(f"CO{contract_letter}")) & (lc["co_slot"] == 1)].copy()
years_avail = sorted(all_years_data["year"].unique())

year_colors = [
    "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c",
    "#3498db", "#9b59b6", "#fd79a8", "#636e72", "#74b9ff", "#a29bfe", "#55efc4",
]

fig2 = go.Figure()
for idx, yr in enumerate(years_avail):
    yd = all_years_data[all_years_data["year"] == yr].copy()
    yd = yd[yd["td_to_expiry"].notna()].sort_values("td_to_expiry", ascending=False)
    is_outlier_yr = tbl[
        (tbl["contract_letter"] == contract_letter) & (tbl["year"] == yr)
    ]["is_outlier"].values
    is_out = bool(is_outlier_yr[0]) if len(is_outlier_yr) > 0 else False
    color = year_colors[idx % len(year_colors)]
    lw = 2.5 if yr == selected_year else (1.2 if not is_out else 2.0)
    dash = "solid" if not is_out else "dash"
    fig2.add_trace(go.Scatter(
        x=yd["td_to_expiry"], y=yd["fly"],
        mode="lines",
        name=str(yr),
        line=dict(color=color, width=lw, dash=dash),
        hovertemplate=f"<b>{yr}</b> DTE%{{x}}: %{{y:.3f}}<extra></extra>",
    ))

# Entry/exit vertical lines
fig2.add_vline(x=3, line=dict(color=SHORT_COLOR, width=1.5, dash="dash"),
               annotation_text="Exit DTE3", annotation_font=dict(color=SHORT_COLOR, size=11))

fig2.add_shape(
    type="rect", x0=3, x1=0,
    y0=0, y1=1, yref="paper",
    fillcolor=SHORT_COLOR, opacity=0.06, line_width=0,
)

fig2.update_layout(
    template=PLOT_TEMPLATE,
    paper_bgcolor=PAPER,
    plot_bgcolor=PAPER,
    height=400,
    xaxis=dict(
        title="Trading Days to Expiry →",
        autorange="reversed",
        showgrid=True, gridcolor=GRID,
        tickfont=dict(size=10, color=SUBTEXT),
    ),
    yaxis=dict(title="Fly Price", showgrid=True, gridcolor=GRID,
               tickfont=dict(size=10, color=SUBTEXT)),
    margin=dict(l=10, r=10, t=20, b=10),
    legend=dict(
        orientation="h", y=-0.15, x=0,
        font=dict(size=10, color=TEXT), bgcolor="rgba(0,0,0,0)",
    ),
    font=dict(color=TEXT),
    hovermode="x unified",
)
fig2.add_annotation(
    text="Dashed = outlier year (against typical direction)",
    xref="paper", yref="paper", x=0, y=1.02,
    showarrow=False, font=dict(size=10, color=SUBTEXT),
)
st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: ANALYSIS TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-header'>Year-by-Year Analysis Table — CO{contract_letter}</div>", unsafe_allow_html=True)

ct = tbl[tbl["contract_letter"] == contract_letter].sort_values("year", ascending=False).copy()

# Round numeric columns
for col in ["pnl", "prev1_fly", "prev2_fly", "bw_td7", "bw_DTE10", "bw_DTE7", "bw_DTE5"]:
    ct[col] = ct[col].round(3)

# Signal columns: classify each into WARNING / CONFIRM / NEUTRAL
typ_label = TYPICAL_DIR[contract_letter][0]
typical_long = "SHORT" not in typ_label or "STRONG_SHORT" not in typ_label
# For N (STRONG_SHORT) and Z (SLIGHT_SHORT): typical direction is short
if "SHORT" in typ_label:
    typical_long = False
else:
    typical_long = True

def classify_prev(val, typical_long):
    if pd.isna(val) or abs(val) < 0.15:
        return "—"
    if typical_long:
        return "✓ CONF" if val > 0 else "⚠ WARN"
    else:
        return "✓ CONF" if val < 0 else "⚠ WARN"

def classify_bw(val, letter):
    # H and X have inverted backw logic
    inverted = letter in ["H", "X"]
    if pd.isna(val) or abs(val) < 0.15:
        return "—"
    if inverted:
        if typical_long:
            return "⚠ WARN" if val > 0.4 else "✓ CONF"
        else:
            return "✓ CONF" if val > 0 else "⚠ WARN"
    else:
        if typical_long:
            return "✓ CONF" if val > 0.15 else ("⚠ WARN" if val < -0.15 else "—")
        else:
            return "✓ CONF" if val < -0.15 else ("⚠ WARN" if val > 0.15 else "—")

ct["p1_sig"] = ct["prev1_fly"].apply(lambda v: classify_prev(v, typical_long))
ct["p2_sig"] = ct["prev2_fly"].apply(lambda v: classify_prev(v, typical_long))
ct["bw_td7_sig"] = ct["bw_td7"].apply(lambda v: classify_bw(v, contract_letter))
ct["bw_DTE10_sig"] = ct["bw_DTE10"].apply(lambda v: classify_bw(v, contract_letter))

# Build display table
display_cols = {
    "year": "Year",
    "direction": "Direction",
    "pnl": "PnL",
    "prev1_fly": f"prev1 ({p1_letter})",
    "p1_sig": "p1 Signal",
    "prev2_fly": f"prev2 ({p2_letter})",
    "p2_sig": "p2 Signal",
    "bw_td7": "bw@td7",
    "bw_td7_sig": "bw@td7 Sig",
    "bw_DTE10": "bw@DTE10",
    "bw_DTE10_sig": "bw@DTE10 Sig",
    "bw_DTE7": "bw@DTE7",
    "bw_DTE5": "bw@DTE5",
    "phase_entry": "Phase",
    "is_outlier": "Outlier?",
}
disp = ct[list(display_cols.keys())].rename(columns=display_cols)

# Color functions for plotly table
def dir_color(v):
    if v == "LONG":
        return LONG_COLOR
    elif v == "SHORT":
        return SHORT_COLOR
    return NEUTRAL_COLOR

def pnl_color(v):
    try:
        return LONG_COLOR if float(v) >= 0 else SHORT_COLOR
    except:
        return TEXT

def sig_color(v):
    if "CONF" in str(v):
        return CONFIRM_COLOR
    elif "WARN" in str(v):
        return WARN_COLOR
    return SUBTEXT

def outlier_color(v):
    return WARN_COLOR if v else TEXT

# Build plotly table
header_vals = list(display_cols.values())

cell_vals = []
cell_colors = []

for col_key, col_label in display_cols.items():
    vals = disp[col_label].tolist()
    cell_vals.append(vals)
    if col_key == "direction":
        cell_colors.append([dir_color(v) for v in vals])
    elif col_key == "pnl":
        cell_colors.append([pnl_color(v) for v in vals])
    elif col_key in ["p1_sig", "p2_sig", "bw_td7_sig", "bw_DTE10_sig"]:
        cell_colors.append([sig_color(v) for v in vals])
    elif col_key == "is_outlier":
        cell_colors.append([outlier_color(v) for v in vals])
    else:
        cell_colors.append([TEXT] * len(vals))

# Row alternating background
row_bg = []
for i in range(len(disp)):
    if disp.iloc[i]["Outlier?"] is True:
        row_bg.append("rgba(248,81,73,0.10)")
    elif i % 2 == 0:
        row_bg.append(TABLE_CELL_BG)
    else:
        row_bg.append(TABLE_ALT_BG)

fig_table = go.Figure(data=[go.Table(
    columnwidth=[50, 75, 60, 75, 75, 75, 75, 75, 85, 80, 90, 70, 70, 100, 70],
    header=dict(
        values=[f"<b>{h}</b>" for h in header_vals],
        fill_color=TABLE_HEADER_BG,
        font=dict(color=TEXT, size=11),
        align="center",
        height=32,
        line=dict(color=BORDER, width=1),
    ),
    cells=dict(
        values=cell_vals,
        fill_color=[row_bg] * len(cell_vals),
        font=dict(color=cell_colors, size=11),
        align=["center"] * len(cell_vals),
        height=30,
        line=dict(color=BORDER, width=0.5),
    ),
)])

fig_table.update_layout(
    paper_bgcolor=PAPER,
    margin=dict(l=0, r=0, t=0, b=0),
    height=min(80 + len(disp) * 32, 600),
)
st.plotly_chart(fig_table, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: PREDICTOR SUMMARY METRICS (quick read)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-header'>Signal Summary</div>", unsafe_allow_html=True)

BEST_PREDICTOR_INFO = {
    "F": ("bw_DTE5", "+0.770 IC", "90%"),
    "G": ("bw_DTE5", "+0.297 IC", "70%"),
    "H": ("bw_DTE7 (inverted)", "−0.650 IC", "60%"),
    "J": ("bw_DTE5", "+0.720 IC", "82%"),
    "K": ("prev1_J (inverted)", "−0.511 IC", "36%"),
    "M": ("bw_DTE7", "+0.173 IC", "73%"),
    "N": ("bw_DTE7", "+0.155 IC", "55%"),
    "Q": ("bw_DTE7", "+0.729 IC", "60%"),
    "U": ("prev1_Q", "+0.480 IC", "80%"),
    "V": ("prev1_U", "+0.774 IC", "89%"),
    "X": ("bw_td7 (inverted)", "−0.480 IC", "67%"),
    "Z": ("bw_DTE5", "+0.248 IC", "38%"),
}
OUTLIER_FINGERPRINT = {
    "F": "backw collapses DTE15→DTE5; 2023 was the cleanest outlier with 3 warning signals",
    "G": "No structural edge — 50/50. Only trade with very strong bw_DTE5 signal",
    "H": "High backw at td7 (>0.5) is a SHORT warning (inverted). Both outliers had bw>0.45",
    "J": "Outlier years show backw decaying from entry to DTE7. 2026: bw 0.69→0.58→0.46",
    "K": "prev1_J > +0.30 with backw > 0.4 = rally exhaustion → SHORT. K22: bw=4.11 extreme",
    "M": "prev1_K disaster (K going strongly negative) precedes M SHORT. M22 prev1=−0.93",
    "N": "Structural SHORT — only backw >1.0 signals a LONG outlier (2019, 2022)",
    "Q": "9/10 LONG — almost no outlier risk. Single 2018 outlier was barely −0.04",
    "U": "bw_td7 >1.0 with fading slope = warning (2025 outlier). prev1_Q most reliable",
    "V": "prev1_U negative = strong SHORT warning (89% accuracy). Momentum echo of U",
    "X": "High backw = SHORT (inverted). bw_td7 >0.6 predicted SHORT in 2019/2021/2022",
    "Z": "No reliable predictor. Skip or size very small",
}

c1, c2, c3 = st.columns(3)
pred_name, pred_ic, pred_sa = BEST_PREDICTOR_INFO[contract_letter]
with c1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Best Predictor</div>
        <div class='metric-value' style='font-size:16px;'>{pred_name}</div>
        <div style='color:{SUBTEXT};font-size:12px;margin-top:4px;'>{pred_ic} &nbsp;|&nbsp; Sign Acc: {pred_sa}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    td_str, wins, total = TYPICAL_DIR[contract_letter]
    tag_class = "tag-long" if "LONG" in td_str else ("tag-short" if "SHORT" in td_str else "tag-mixed")
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Typical Direction</div>
        <div class='metric-value'><span class='{tag_class}'>{td_str.replace('_', ' ')}</span></div>
        <div style='color:{SUBTEXT};font-size:12px;margin-top:6px;'>{wins}/{total} years ({int(wins/total*100)}%)</div>
    </div>""", unsafe_allow_html=True)
with c3:
    outlier_count = tbl[tbl["contract_letter"] == contract_letter]["is_outlier"].sum()
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Outlier Years</div>
        <div class='metric-value'>{int(outlier_count)} / {total}</div>
        <div style='color:{SUBTEXT};font-size:12px;margin-top:4px;'>Against typical direction</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""<div style='background:{CARD}; border:1px solid {BORDER}; border-radius:10px;
    padding:14px 18px; margin-top:4px;'>
    <div class='metric-label' style='margin-bottom:6px;'>Outlier Fingerprint</div>
    <div style='color:{TEXT}; font-size:13px; line-height:1.6;'>{OUTLIER_FINGERPRINT[contract_letter]}</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: CROSS-CONTRACT OVERVIEW TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("Cross-Contract Overview (all 12)", expanded=False):
    cross_data = {
        "Contract": ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"],
        "Typical Dir": ["LEAN LONG", "MIXED", "STRONG LONG", "SLIGHT LONG", "LEAN LONG",
                        "STRONG LONG", "STRONG SHORT", "STRONG LONG", "LEAN LONG",
                        "SLIGHT LONG", "SLIGHT LONG", "SLIGHT SHORT"],
        "Score": ["7/10", "5/10", "8/10", "6/11", "7/11", "8/11", "2/11",
                  "9/10", "7/10", "6/10", "6/10", "4/10"],
        "Win%": ["70%", "50%", "80%", "55%", "64%", "73%", "18%",
                 "90%", "70%", "60%", "60%", "40%"],
        "Best Predictor": [
            "bw_DTE5 (90%)", "bw_DTE5 (70%)", "bw_DTE7 inverted (60%)",
            "bw_DTE5 (82%)", "prev1_J inverted (36%)", "bw_DTE7 (73%)",
            "bw_DTE7 (55%)", "bw_DTE7 (60%)", "prev1_Q (80%)",
            "prev1_U (89%)", "bw_td7 inverted (67%)", "bw_DTE5 (38%)",
        ],
        "Obs Months": [
            "Sep–Nov", "Oct–Dec", "Nov–Jan", "Dec–Feb", "Jan–Mar", "Feb–Apr",
            "Mar–May", "Apr–Jun", "May–Jul", "Jun–Aug", "Jul–Sep", "Aug–Oct",
        ],
    }
    cross_df = pd.DataFrame(cross_data)

    dir_colors_cross = []
    for d in cross_df["Typical Dir"]:
        if "LONG" in d:
            dir_colors_cross.append(LONG_COLOR)
        elif "SHORT" in d:
            dir_colors_cross.append(SHORT_COLOR)
        else:
            dir_colors_cross.append(NEUTRAL_COLOR)

    win_colors_cross = []
    for w in cross_df["Win%"]:
        pct = int(w.replace("%", ""))
        if pct >= 70:
            win_colors_cross.append(LONG_COLOR)
        elif pct <= 45:
            win_colors_cross.append(SHORT_COLOR)
        else:
            win_colors_cross.append(WARN_COLOR)

    row_bg_cross = [TABLE_CELL_BG if i % 2 == 0 else TABLE_ALT_BG for i in range(len(cross_df))]
    # Highlight selected contract
    for i, c in enumerate(cross_df["Contract"]):
        if c == contract_letter:
            row_bg_cross[i] = "rgba(56,139,253,0.13)"

    fig_cross = go.Figure(data=[go.Table(
        columnwidth=[50, 110, 60, 60, 200, 100],
        header=dict(
            values=["<b>" + c + "</b>" for c in cross_df.columns],
            fill_color=TABLE_HEADER_BG,
            font=dict(color=TEXT, size=11),
            align="center",
            height=30,
            line=dict(color=BORDER, width=1),
        ),
        cells=dict(
            values=[cross_df[c].tolist() for c in cross_df.columns],
            fill_color=[row_bg_cross] * len(cross_df.columns),
            font=dict(
                color=[
                    [TEXT] * len(cross_df),
                    dir_colors_cross,
                    [TEXT] * len(cross_df),
                    win_colors_cross,
                    [TEXT] * len(cross_df),
                    [SUBTEXT] * len(cross_df),
                ],
                size=11,
            ),
            align=["center"] * len(cross_df.columns),
            height=28,
            line=dict(color=BORDER, width=0.5),
        ),
    )])
    fig_cross.update_layout(
        paper_bgcolor=PAPER,
        margin=dict(l=0, r=0, t=0, b=0),
        height=420,
    )
    st.plotly_chart(fig_cross, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-top:24px; padding-top:12px; border-top:1px solid {BORDER};
text-align:center; color:{SUBTEXT}; font-size:11px;'>
Brent Expiry Fly Dashboard &nbsp;|&nbsp; Entry: td7 &nbsp;|&nbsp; Exit: DTE3 &nbsp;|&nbsp;
Fly = CO_front − 2×CO_center + CO_back &nbsp;|&nbsp; 2016–2026
</div>
""", unsafe_allow_html=True)
