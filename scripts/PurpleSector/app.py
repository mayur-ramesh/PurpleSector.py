import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

# ─── CACHE SETUP ────────────────────────────────────────────────────────────
# Use a local (non-OneDrive) path to avoid SQLite lock / I/O errors from sync.
F1_CACHE_DIR = r"C:\Temp\f1_cache"

@st.cache_resource
def setup_cache():
    os.makedirs(F1_CACHE_DIR, exist_ok=True)
    fastf1.Cache.enable_cache(F1_CACHE_DIR)

setup_cache()

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PurpleSector",
    page_icon="🟣",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── GLOBAL CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

/* Root theme */
:root {
    --purple: #9b59b6;
    --purple-light: #c39bd3;
    --purple-dark: #6c3483;
    --bg: #080808;
    --surface: #111111;
    --surface2: #1a1a1a;
    --border: #2a2a2a;
    --text: #e8e8e8;
    --text-muted: #888888;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Main container */
.main .block-container {
    background-color: var(--bg);
    padding-top: 1.5rem;
    max-width: 1400px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Sidebar header brand */
.sidebar-brand {
    text-align: center;
    padding: 1.2rem 0 0.8rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.2rem;
}
.sidebar-brand h1 {
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: -0.5px;
    margin: 0;
    background: linear-gradient(135deg, #9b59b6, #c39bd3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sidebar-brand p {
    font-size: 0.7rem;
    color: var(--text-muted) !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0.2rem 0 0 0;
}

/* Page header */
.page-header {
    border-left: 4px solid var(--purple);
    padding-left: 1rem;
    margin-bottom: 1.5rem;
}
.page-header h2 {
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0;
    color: var(--text);
}
.page-header p {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin: 0.2rem 0 0 0;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
}
div[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--purple-light) !important;
    font-weight: 700;
}

/* Buttons */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--purple-dark), var(--purple)) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 2rem !important;
    transition: opacity 0.2s ease, transform 0.1s ease !important;
    letter-spacing: 0.3px;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* Inputs & selects */
div[data-testid="stSelectbox"] > div, div[data-testid="stTextInput"] > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    border-radius: 6px !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Spinner */
div[data-testid="stSpinner"] { color: var(--purple) !important; }

/* Info / error boxes */
div[data-testid="stAlert"] {
    border-radius: 6px !important;
    border: 1px solid var(--border) !important;
}

/* Plot backgrounds */
.element-container iframe { border-radius: 8px; }

/* Nav tab pills */
div[data-testid="stRadio"] > div { gap: 0.4rem; }
div[data-testid="stRadio"] label {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.35rem 1rem;
    cursor: pointer;
    font-size: 0.85rem;
    transition: background 0.2s;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: var(--purple) !important;
    border-color: var(--purple) !important;
    color: white !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR BRAND ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h1>🟣 PurpleSector</h1>
        <p>F1 Qualifying Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏎️  Qualifying Battle", "📊  The Delta", "⏱️  Lap Time Ladder"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**⚙️ Session**")
    year = st.selectbox("Year", range(2026, 2017, -1), index=0)
    gp   = st.text_input("Grand Prix", "Australia", placeholder="e.g. Monaco, Silverstone")
    session_type = st.selectbox("Session", ['Q', 'R', 'SQ', 'FP1', 'FP2', 'FP3'])

# ─── DATA LOADER (CACHED) ────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_session(year, gp, session_type):
    try:
        s = fastf1.get_session(year, gp, session_type)
        s.load()
        return s
    except Exception as e:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — QUALIFYING BATTLE
# ═══════════════════════════════════════════════════════════════════════════════
if "Qualifying Battle" in page:
    st.markdown("""
    <div class="page-header">
        <h2>🏎️ Qualifying Battle</h2>
        <p>Compare fastest lap telemetry between any two drivers — speed, throttle, and delta.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(f"Loading {gp} {year} {session_type}…"):
        session = load_session(year, gp, session_type)

    if session is None:
        st.error(f"Couldn't load **{gp} {year} {session_type}**. Check the Grand Prix spelling.")
        st.stop()

    driver_list = sorted(session.results['Abbreviation'].dropna().unique().tolist())

    with st.sidebar:
        st.markdown("**👤 Drivers**")
        d1 = st.selectbox("Driver 1", driver_list, index=0, key="qb_d1")
        d2 = st.selectbox("Driver 2", driver_list, index=min(1, len(driver_list)-1), key="qb_d2")

    run = st.button("⚡ Analyze Telemetry", key="qb_run")

    if run:
        if d1 == d2:
            st.warning("Please select two different drivers.")
            st.stop()
        try:
            with st.spinner("Crunching telemetry…"):
                lap_d1 = session.laps.pick_driver(d1).pick_fastest()
                lap_d2 = session.laps.pick_driver(d2).pick_fastest()
                tel_d1 = lap_d1.get_car_data().add_distance()
                tel_d2 = lap_d2.get_car_data().add_distance()
                circuit_info = session.get_circuit_info()

            # ── Sector Metrics ────────────────────────────────────────────────
            s1 = (lap_d1['Sector1Time'] - lap_d2['Sector1Time']).total_seconds()
            s2 = (lap_d1['Sector2Time'] - lap_d2['Sector2Time']).total_seconds()
            s3 = (lap_d1['Sector3Time'] - lap_d2['Sector3Time']).total_seconds()
            tot= (lap_d1['LapTime']     - lap_d2['LapTime']).total_seconds()

            def fmt_delta(val):
                sign = "+" if val > 0 else ""
                return f"{sign}{val:.3f}s"

            def winner(val, a, b):
                return a if val < 0 else b

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Lap Gap", fmt_delta(tot),
                        help=f"{d1} vs {d2} — negative means {d1} is faster")
            col2.metric(f"Sector 1 → {winner(s1,d1,d2)}", fmt_delta(s1))
            col3.metric(f"Sector 2 → {winner(s2,d1,d2)}", fmt_delta(s2))
            col4.metric(f"Sector 3 → {winner(s3,d1,d2)}", fmt_delta(s3))

            # ── Plotting ──────────────────────────────────────────────────────
            fastf1.plotting.setup_mpl(color_scheme='fastf1')
            c1 = fastf1.plotting.get_team_color(lap_d1['Team'], session=session)
            c2 = fastf1.plotting.get_team_color(lap_d2['Team'], session=session)

            fig, axes = plt.subplots(
                3, 1, figsize=(14, 11), sharex=True,
                gridspec_kw={'height_ratios': [3, 1, 1]},
                facecolor='#0a0a0a'
            )
            for ax in axes:
                ax.set_facecolor('#0f0f0f')
                ax.tick_params(colors='#aaaaaa')
                for spine in ax.spines.values():
                    spine.set_color('#2a2a2a')

            # Plot 1: Speed
            axes[0].plot(tel_d1['Distance'], tel_d1['Speed'], color=c1,
                         label=d1, linewidth=2)
            axes[0].plot(tel_d2['Distance'], tel_d2['Speed'], color=c2,
                         label=d2, linewidth=2, linestyle='--')
            axes[0].set_ylabel('Speed (km/h)', color='#aaaaaa')
            axes[0].legend(facecolor='#1a1a1a', edgecolor='#333333',
                           labelcolor='white', fontsize=10)
            axes[0].set_title(
                f"{session.event['EventName']} {year} — {d1} vs {d2}",
                color='white', fontsize=13, fontweight='600', pad=10
            )
            axes[0].grid(True, linestyle='--', linewidth=0.4, color='#2a2a2a')

            # Corner annotations
            if circuit_info is not None:
                y_top = tel_d1['Speed'].max() + 12
                for _, corner in circuit_info.corners.iterrows():
                    txt = f"{corner['Number']}{corner['Letter']}"
                    axes[0].text(corner['Distance'], y_top, txt,
                                 va='center', ha='center', fontsize=7.5,
                                 color='white',
                                 bbox=dict(facecolor='#2d1b4e', edgecolor='#6c3483',
                                           alpha=0.9, boxstyle='round,pad=0.2'))
                    for ax in [axes[0], axes[2]]:
                        ax.axvline(corner['Distance'], color='#333333',
                                   linestyle=':', alpha=0.5, linewidth=0.8)

            # Plot 2: Throttle
            axes[1].plot(tel_d1['Distance'], tel_d1['Throttle'], color=c1, label=d1)
            axes[1].plot(tel_d2['Distance'], tel_d2['Throttle'], color=c2,
                         label=d2, linestyle='--')
            axes[1].set_ylabel('Throttle %', color='#aaaaaa')
            axes[1].set_yticks([0, 50, 100])
            axes[1].grid(True, axis='x', linestyle='--', linewidth=0.4, color='#2a2a2a')

            # Plot 3: Speed Delta
            d2_interp = np.interp(tel_d1['Distance'], tel_d2['Distance'], tel_d2['Speed'])
            delta = tel_d1['Speed'] - d2_interp
            axes[2].plot(tel_d1['Distance'], delta, color='#dddddd', linewidth=1)
            axes[2].axhline(0, color='#555555', linestyle='--', linewidth=1)
            axes[2].fill_between(tel_d1['Distance'], delta, 0,
                                 where=delta > 0, facecolor=c1, alpha=0.45)
            axes[2].fill_between(tel_d1['Distance'], delta, 0,
                                 where=delta < 0, facecolor=c2, alpha=0.45)
            axes[2].set_ylabel(f'Δ Speed (km/h)\n(+) {d1} faster', color='#aaaaaa')
            axes[2].set_xlabel('Distance (m)', color='#aaaaaa')
            axes[2].grid(True, linestyle='--', linewidth=0.4, color='#2a2a2a')

            plt.tight_layout(rect=[0, 0, 1, 0.98])
            st.pyplot(fig)
            plt.close(fig)

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.info("Tip: Make sure both drivers completed a valid lap in this session.")
    else:
        st.info("Select your session and drivers in the sidebar, then click **⚡ Analyze Telemetry**.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — THE DELTA
# ═══════════════════════════════════════════════════════════════════════════════
elif "The Delta" in page:
    st.markdown("""
    <div class="page-header">
        <h2>📊 The Delta</h2>
        <p>Season-long qualifying gap between two drivers across all rounds. Uses the deepest common session (Q3 → Q2 → Q1).</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("**👤 Drivers**")
        ref_driver  = st.text_input("Reference Driver", "VER",
                                    help="3-letter abbreviation, e.g. VER").upper()
        comp_driver = st.text_input("Comparison Driver", "NOR").upper()

    run_delta = st.button("📊 Build Delta Chart", key="delta_run")

    if run_delta:
        progress = st.progress(0, text="Loading rounds…")
        data = []

        color_ref  = '#808080'
        color_comp = '#ffffff'

        rounds = list(range(1, 30))
        loaded = 0

        for i, r in enumerate(rounds):
            try:
                s = fastf1.get_session(year, r, 'Q')
                s.load(telemetry=False, weather=False, messages=False)

                # Grab colors once
                try:
                    color_ref  = fastf1.plotting.get_driver_color(ref_driver, session=s)
                    color_comp = fastf1.plotting.get_driver_color(comp_driver, session=s)
                except Exception:
                    pass

                race_name = s.event.EventName.replace(' Grand Prix', '').replace(f' {year}', '')
                res = s.results

                if ref_driver not in res['Abbreviation'].values or \
                   comp_driver not in res['Abbreviation'].values:
                    continue

                d1_row = res.loc[res['Abbreviation'] == ref_driver].iloc[0]
                d2_row = res.loc[res['Abbreviation'] == comp_driver].iloc[0]

                t1 = t2 = None
                session_used = "None"

                for seg in ['Q3', 'Q2', 'Q1']:
                    if not pd.isnull(d1_row[seg]) and not pd.isnull(d2_row[seg]):
                        t1, t2 = d1_row[seg], d2_row[seg]
                        session_used = seg
                        break

                if t1 is None:
                    continue

                gap = t2.total_seconds() - t1.total_seconds()
                data.append({
                    'Round': r,
                    'Race':  race_name,
                    'Gap':   gap,
                    'Color': color_comp if gap < 0 else color_ref,
                    'Seg':   session_used
                })
                loaded += 1

            except Exception:
                pass  # Round doesn't exist or not yet raced

            progress.progress(min((i + 1) / len(rounds), 1.0),
                              text=f"Round {r} checked…")

        progress.empty()

        if not data:
            st.error(f"No data found for **{ref_driver}** vs **{comp_driver}** in {year}. Check driver codes.")
            st.stop()

        df = pd.DataFrame(data)

        # ── Plot ──────────────────────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(max(12, len(df) * 0.9), 7),
                                facecolor='#0a0a0a')
        ax.set_facecolor('#0a0a0a')

        bars = ax.bar(range(len(df)), df['Gap'], color=df['Color'],
                      edgecolor='#333333', linewidth=0.6, width=0.7)

        # Trend line
        if len(df) > 2:
            z = np.polyfit(range(len(df)), df['Gap'], 1)
            p = np.poly1d(z)
            ax.plot(range(len(df)), p(range(len(df))),
                    color='#9b59b6', linestyle='--', linewidth=2.5,
                    alpha=0.9, label='Trend', zorder=5)

        ax.axhline(0, color='#555555', linewidth=1.2, alpha=0.8)

        # Bar value labels
        for bar, row in zip(bars, df.itertuples()):
            h = bar.get_height()
            y = h + 0.02 if h >= 0 else h - 0.07
            ax.text(bar.get_x() + bar.get_width() / 2, y,
                    f"{abs(row.Gap):.3f}",
                    ha='center', va='bottom' if h >= 0 else 'top',
                    fontsize=7.5, color='white', fontweight='600')
            # Session badge
            ax.text(bar.get_x() + bar.get_width() / 2,
                    0.01 if h >= 0 else -0.01,
                    row.Seg,
                    ha='center', va='bottom' if h >= 0 else 'top',
                    fontsize=6, color='#888888')

        # Axes styling
        tick_labels = [f"R{row.Round}\n{row.Race[:3].upper()}"
                        for row in df.itertuples()]
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(tick_labels, fontsize=9, color='#cccccc')
        ax.tick_params(axis='y', colors='#aaaaaa')
        ax.set_ylabel(f"Gap (s)   +{ref_driver} faster  /  +{comp_driver} faster",
                       color='#aaaaaa', fontsize=11)
        ax.set_title(f"{year} Qualifying Gap — {ref_driver} vs {comp_driver}",
                      color='white', fontsize=14, fontweight='700', pad=14)

        for spine in ax.spines.values():
            spine.set_color('#2a2a2a')
        ax.grid(axis='y', alpha=0.12, color='#888888', linestyle='--')

        # Legend
        patches = [
            mpatches.Patch(color=color_comp, label=f'{comp_driver} faster'),
            mpatches.Patch(color=color_ref,  label=f'{ref_driver} faster'),
            mpatches.Patch(color='#9b59b6',  label='Trend'),
        ]
        leg = ax.legend(handles=patches, facecolor='#1a1a1a',
                         edgecolor='#333333', fontsize=9)
        for t in leg.get_texts():
            t.set_color('white')

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # Summary table
        st.markdown("---")
        st.markdown(f"**{comp_driver} faster in:** {(df['Gap'] < 0).sum()} rounds &nbsp;|&nbsp;"
                    f"**{ref_driver} faster in:** {(df['Gap'] > 0).sum()} rounds &nbsp;|&nbsp;"
                    f"**Avg gap:** {df['Gap'].mean():+.3f}s",
                    unsafe_allow_html=True)
    else:
        st.info("Enter two driver codes and click **📊 Build Delta Chart**.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — LAP TIME LADDER
# ═══════════════════════════════════════════════════════════════════════════════
elif "Lap Time Ladder" in page:
    st.markdown("""
    <div class="page-header">
        <h2>⏱️ Lap Time Ladder</h2>
        <p>All drivers' personal best lap times for the selected session, ranked fastest → slowest and coloured by team.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(f"Loading {gp} {year} {session_type}…"):
        session = load_session(year, gp, session_type)

    if session is None:
        st.error(f"Couldn't load **{gp} {year} {session_type}**. Check the Grand Prix spelling.")
        st.stop()

    if st.button("⏱️ Build Lap Ladder", key="ladder_run"):
        try:
            with st.spinner("Processing laps…"):
                laps = session.laps.copy()
                laps = laps[laps['LapTime'].notna()]

                # Best lap per driver
                best = (laps.groupby('Driver')['LapTime']
                            .min()
                            .reset_index()
                            .sort_values('LapTime'))
                best['LapTime_s']   = best['LapTime'].dt.total_seconds()
                best['Gap_to_P1']   = best['LapTime_s'] - best['LapTime_s'].iloc[0]
                best['Gap_fmt']     = best['Gap_to_P1'].apply(
                    lambda x: "POLE" if x == 0 else f"+{x:.3f}s"
                )

                # Attach team for colors
                driver_team = (laps.dropna(subset=['Team'])
                                   .groupby('Driver')['Team']
                                   .first()
                                   .to_dict())
                best['Team'] = best['Driver'].map(driver_team)

            fastf1.plotting.setup_mpl(color_scheme='fastf1')

            def safe_team_color(team):
                try:
                    return fastf1.plotting.get_team_color(team, session=session)
                except Exception:
                    return '#888888'

            best['Color'] = best['Team'].apply(safe_team_color)

            fig, ax = plt.subplots(figsize=(10, max(8, len(best) * 0.52)),
                                    facecolor='#0a0a0a')
            ax.set_facecolor('#0a0a0a')

            y_pos = range(len(best) - 1, -1, -1)   # Fastest at top

            bars = ax.barh(list(y_pos), best['Gap_to_P1'], color=best['Color'].tolist(),
                           edgecolor='#222222', linewidth=0.5, height=0.7)

            # Driver name labels
            for idx, (yp, row) in enumerate(zip(y_pos, best.itertuples())):
                ax.text(-0.03, yp, f"P{idx+1}  {row.Driver}",
                        va='center', ha='right', fontsize=10,
                        color=row.Color, fontweight='600')
                ax.text(row.Gap_to_P1 + 0.01, yp, row.Gap_fmt,
                        va='center', ha='left', fontsize=9, color='#cccccc')

            ax.set_yticks([])
            ax.set_xlabel('Gap to Pole (s)', color='#aaaaaa', fontsize=11)
            ax.set_title(
                f"{session.event['EventName']} {year} — {session_type} Lap Time Ladder",
                color='white', fontsize=13, fontweight='700', pad=12
            )
            ax.tick_params(colors='#aaaaaa')
            for spine in ax.spines.values():
                spine.set_color('#2a2a2a')
            ax.grid(axis='x', alpha=0.12, color='#888888', linestyle='--')
            left_margin = best['Driver'].str.len().max() * 0.065
            ax.set_xlim(-left_margin, best['Gap_to_P1'].max() * 1.25)

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # Clean table
            st.markdown("---")
            table = best[['Driver', 'Team', 'LapTime_s', 'Gap_fmt']].copy()
            table.insert(0, 'Pos', range(1, len(table) + 1))
            table['Best Lap'] = table['LapTime_s'].apply(
                lambda s: f"{int(s // 60)}:{s % 60:06.3f}"
            )
            table = table.rename(columns={'Gap_fmt': 'Gap'})[['Pos', 'Driver', 'Team', 'Best Lap', 'Gap']]
            st.dataframe(table, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Failed to build lap ladder: {e}")
    else:
        st.info("Click **⏱️ Build Lap Ladder** to rank all drivers.")
