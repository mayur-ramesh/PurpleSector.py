import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# 1. SETUP
if not os.path.exists('cache'):
    os.makedirs('cache')
fastf1.Cache.enable_cache('cache') 

def analyze_battle(year, gp, session_type):
    print(f"Loading {year} {gp} {session_type}...")
    
    # 2. LOAD DATA
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    circuit_info = session.get_circuit_info() # Get official corner data
    
    # 3. IDENTIFY DRIVERS
    fastest_lap = session.laps.pick_fastest()
    pole_driver = fastest_lap['Driver']
    pole_team = fastest_lap['Team']
    
    # Find P2 (Second fastest)
    drivers = session.results
    p2_driver_code = drivers.iloc[1]['Abbreviation']
    p2_lap = session.laps.pick_driver(p2_driver_code).pick_fastest()
    p2_team = p2_lap['Team']
    
    print(f" BATTLE: {pole_driver} vs {p2_driver_code}")

    # SECTOR WISE ANALYSIS (Text Report) 
    print("\n--- SECTOR GAPS ---")
    for i in [1, 2, 3]:
        s_pole = fastest_lap[f'Sector{i}Time'].total_seconds()
        s_p2 = p2_lap[f'Sector{i}Time'].total_seconds()
        gap = s_pole - s_p2
        leader = pole_driver if gap < 0 else p2_driver_code
        print(f"Sector {i}: {leader} was faster by {abs(gap):.3f}s")
    print("----------------------\n")

    # 4. TELEMETRY
    d1_tel = fastest_lap.get_car_data().add_distance()
    d2_tel = p2_lap.get_car_data().add_distance()

    # 5. PLOTTING
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    
    # Create 3 subplots: Speed, Throttle, and Speed Delta
    fig, ax = plt.subplots(3, 1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})
    
    d1_color = fastf1.plotting.get_team_color(pole_team, session=session)
    d2_color = fastf1.plotting.get_team_color(p2_team, session=session)
    
    # PLOT 1: SPEED TRACE 
    ax[0].plot(d1_tel['Distance'], d1_tel['Speed'], color=d1_color, label=pole_driver, linewidth=2)
    ax[0].plot(d2_tel['Distance'], d2_tel['Speed'], color=d2_color, label=p2_driver_code, linestyle='--', linewidth=2)
    ax[0].set_ylabel('Speed (km/h)')
    ax[0].legend(loc='lower right')
    ax[0].set_title(f"Battle for Pole: {pole_driver} vs {p2_driver_code} | {session.event['EventName']} {year}", fontsize=14)

    # This adds the corner numbers to the top of the graph
    if circuit_info is not None:
        y_pos = d1_tel['Speed'].max() + 10 
        for _, corner in circuit_info.corners.iterrows():
            txt = f"{corner['Number']}{corner['Letter']}"
            ax[0].text(corner['Distance'], y_pos, txt, 
                       va='center', ha='center', fontsize=9, color='white', 
                       bbox=dict(facecolor='#202020', edgecolor='none', alpha=0.8))
            ax[0].axvline(x=corner['Distance'], color='gray', linestyle=':', alpha=0.3)
            ax[2].axvline(x=corner['Distance'], color='gray', linestyle=':', alpha=0.3)

    # --- PLOT 2: THROTTLE ---
    ax[1].plot(d1_tel['Distance'], d1_tel['Throttle'], color=d1_color, label=pole_driver)
    ax[1].plot(d2_tel['Distance'], d2_tel['Throttle'], color=d2_color, label=p2_driver_code, linestyle='--')
    ax[1].set_ylabel('Throttle %')
    ax[1].set_yticks([0, 100])

    # --- PLOT 3: SPEED DELTA (Who is faster?) ---
    # Interpolate P2 to match P1's distance
    d2_speed_interp = np.interp(d1_tel['Distance'], d2_tel['Distance'], d2_tel['Speed'])
    delta = d1_tel['Speed'] - d2_speed_interp
    
    ax[2].plot(d1_tel['Distance'], delta, color='white', linewidth=1)
    ax[2].axhline(0, color='gray', linestyle='--', linewidth=1) # The "Even" line
    ax[2].fill_between(d1_tel['Distance'], delta, 0, where=delta>0, facecolor=d1_color, alpha=0.5)
    ax[2].fill_between(d1_tel['Distance'], delta, 0, where=delta<0, facecolor=d2_color, alpha=0.5)
    
    ax[2].set_ylabel(f'Delta (km/h)\n(+ {pole_driver} Faster)')
    ax[2].set_xlabel('Distance (m)')

    plt.tight_layout()
    plt.savefig('quali_chart_2026_aus.png', dpi=300)
    print("Chart saved to quali_chart_2026_aus.png")

# RUN IT
analyze_battle(2026, 'Australia', 'Q')