import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="F1 Telemetry Battle", page_icon="🏎️", layout="wide")

# 2. CACHE SETUP (Critical for speed)
# We use Streamlit's cache decorator so we don't re-download data on every click
@st.cache_resource
def setup_cache():
    cache_dir = 'f1_cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)

setup_cache()

# 3. SIDEBAR SELECTION
st.sidebar.header("🏁 Session Config")
year = st.sidebar.selectbox("Year", range(2024, 2017, -1), index=0)
gp = st.sidebar.text_input("Grand Prix (e.g. 'Monaco', 'Silverstone')", "Monaco")
session_type = st.sidebar.selectbox("Session", ['Q', 'R', 'SQ', 'FP1', 'FP2', 'FP3'])

# 4. LOAD DATA FUNCTION
@st.cache_data
def load_session_data(year, gp, session_type):
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
        return session
    except Exception as e:
        return None

# Load the session immediately when the user changes sidebar inputs
with st.spinner(f"Loading {gp} {year} data... (This can take 30s)"):
    session = load_session_data(year, gp, session_type)

if session is None:
    st.error(f"Could not load data for {gp} {year}. Please check the spelling.")
    st.stop()

# 5. DRIVER SELECTION
# Get list of drivers who participated
driver_list = sorted(session.results['Abbreviation'].unique())

st.sidebar.markdown("---")
st.sidebar.header("⚔️ Head-to-Head")
d1 = st.sidebar.selectbox("Driver 1", driver_list, index=0) # Default to first driver
d2 = st.sidebar.selectbox("Driver 2", driver_list, index=1) # Default to second driver

# 6. MAIN ANALYSIS BUTTON
if st.button("Analyze Telemetry", type="primary"):
    
    # --- DATA PROCESSING ---
    try:
        # Get Fastest Laps
        lap_d1 = session.laps.pick_driver(d1).pick_fastest()
        lap_d2 = session.laps.pick_driver(d2).pick_fastest()
        
        # Get Telemetry
        tel_d1 = lap_d1.get_car_data().add_distance()
        tel_d2 = lap_d2.get_car_data().add_distance()
        
        # Calculate Delta (Interpolation)
        d2_interp = np.interp(tel_d1['Distance'], tel_d2['Distance'], tel_d2['Speed'])
        delta = tel_d1['Speed'] - d2_interp
        
        # --- UI LAYOUT ---
        st.title(f"Telemetry Battle: {d1} vs {d2}")
        st.caption(f"{session.event['EventName']} {year} - {session.name}")

        # Metrics Row (Sector Gaps)
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate Sector Deltas
        s1_delta = lap_d1['Sector1Time'] - lap_d2['Sector1Time']
        s2_delta = lap_d1['Sector2Time'] - lap_d2['Sector2Time']
        s3_delta = lap_d1['Sector3Time'] - lap_d2['Sector3Time']
        total_delta = lap_d1['LapTime'] - lap_d2['LapTime']

        col1.metric("Lap Delta", f"{total_delta.total_seconds():.3f}s", 
                    delta_color="inverse") # Red if slower (positive), Green if faster (negative)
        
        col2.metric("Sector 1", f"{s1_delta.total_seconds():.3f}s", delta_color="inverse")
        col3.metric("Sector 2", f"{s2_delta.total_seconds():.3f}s", delta_color="inverse")
        col4.metric("Sector 3", f"{s3_delta.total_seconds():.3f}s", delta_color="inverse")

        # PLOTTING 
        fastf1.plotting.setup_mpl(color_scheme='fastf1')
        fig, ax = plt.subplots(3, 1, figsize=(10, 12), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})
        
        c1 = fastf1.plotting.get_team_color(lap_d1['Team'], session=session)
        c2 = fastf1.plotting.get_team_color(lap_d2['Team'], session=session)

        # Plot 1: Speed
        ax[0].plot(tel_d1['Distance'], tel_d1['Speed'], color=c1, label=d1)
        ax[0].plot(tel_d2['Distance'], tel_d2['Speed'], color=c2, label=d2, linestyle='--')
        ax[0].set_ylabel("Speed (km/h)")
        ax[0].legend()
        ax[0].grid(True, which='both', linestyle='--', linewidth=0.5)

        # Add Corner Labels
        circuit_info = session.get_circuit_info()
        if circuit_info is not None:
            for _, corner in circuit_info.corners.iterrows():
                txt = f"{corner['Number']}{corner['Letter']}"
                ax[0].axvline(x=corner['Distance'], color='gray', linestyle=':', alpha=0.5)
                ax[0].text(corner['Distance'], tel_d1['Speed'].max() + 5, txt, 
                           va='center', ha='center', fontsize=8, color='white')

        # Plot 2: Throttle
        ax[1].plot(tel_d1['Distance'], tel_d1['Throttle'], color=c1, label=d1)
        ax[1].plot(tel_d2['Distance'], tel_d2['Throttle'], color=c2, label=d2, linestyle='--')
        ax[1].set_ylabel("Throttle %")
        ax[1].set_yticks([0, 100])
        ax[1].grid(True, axis='x', linestyle='--', linewidth=0.5)

        # Plot 3: Delta
        ax[2].plot(tel_d1['Distance'], delta, color='white', linewidth=1)
        ax[2].axhline(0, color='gray', linestyle='--')
        ax[2].fill_between(tel_d1['Distance'], delta, 0, where=delta>0, facecolor=c1, alpha=0.5)
        ax[2].fill_between(tel_d1['Distance'], delta, 0, where=delta<0, facecolor=c2, alpha=0.5)
        ax[2].set_ylabel(f"Gap (km/h)\n(+ {d1} Faster)")
        ax[2].set_xlabel("Distance (m)")
        ax[2].grid(True, which='both', linestyle='--', linewidth=0.5)

        # Render the plot in Streamlit
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        st.write("Tip: Try checking if both drivers completed a valid lap in this session.")

else:
    st.info("Select drivers and click 'Analyze Telemetry' to start.")