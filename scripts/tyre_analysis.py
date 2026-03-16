import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# --- 1. Setup & Configuration ---
# Set up dark mode for matplotlib right from the start
plt.style.use('dark_background')

# Configure fastf1 plotting (optional but helps with some defaults)
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
fastf1.Cache.enable_cache('cache')

# Define colors to match the reference image closely
colors = {
    'bg_outer': '#121212',   # Very dark background for the figure outside axes
    'bg_inner': '#1e1e1e',   # Slightly lighter background for the plot area
    'MEDIUM': '#ffd12b',     # Vibrant Yellow
    'HARD': '#e0e0e0',       # Light Grey/White
    'SOFT': '#ff3333',       # Red (just in case)
    'text_dark': 'black',    # For text inside bright bars
    'text_light': 'white',   # For labels on background
    'marker_bg': '#333333'   # Background color for the "Lap X" boxes
}

# --- 2. Load Data ---
session = fastf1.get_session(2025, 'Abu Dhabi', 'R')
session.load()

# Drivers in the order they appear in the image (Top to Bottom)
driver_order = ['LEC', 'NOR', 'PIA', 'VER']
total_laps = session.total_laps

# --- 3. Process Data for Visualization ---
stint_bars = []
pit_stop_markers = []

for i, driver in enumerate(driver_order):
    # Get driver laps
    laps = session.laps.pick_driver(driver)
    
    # Group by stint to get segments
    grouped_stints = laps.groupby('Stint')
    num_stints = grouped_stints.ngroups
    
    for stint_idx, (stint_num, stint_data) in enumerate(grouped_stints):
        compound = stint_data['Compound'].iloc[0]
        start_lap = stint_data['LapNumber'].min()
        end_lap = stint_data['LapNumber'].max()
        
        # Calculate visual start point and duration
        # Stint 1 technically starts at lap 0 for visual purposes
        visual_start = 0 if stint_idx == 0 else start_lap - 1.0
        duration = end_lap - visual_start
        
        # 1. Data for the Horizontal Bar
        stint_bars.append({
            'y_pos': i, # Use index for Y position to control order easily
            'driver': driver,
            'compound': compound,
            'start': visual_start,
            'duration': duration,
            'color': colors.get(compound, 'grey'),
            'text_color': colors['text_dark']
        })
        
        # 2. Data for Pit Stop Marker (if it's not the very last stint)
        if stint_idx < num_stints - 1:
            pit_stop_markers.append({
                'y_pos': i,
                'lap': end_lap,
                'driver': driver
            })

# --- 4. Plotting ---
fig, ax = plt.subplots(figsize=(16, 7))

# Set background colors
fig.patch.set_facecolor(colors['bg_outer'])
ax.set_facecolor(colors['bg_inner'])

# A. Draw vertical dashed lines for ALL pit stops across the board first
# Get unique pit lap numbers across all drivers
unique_pit_laps = sorted(list(set(p['lap'] for p in pit_stop_markers)))
for lap in unique_pit_laps:
    ax.axvline(x=lap, color='white', linestyle='--', linewidth=1, alpha=0.25)

# B. Draw the Horizontal Stint Bars
for bar in stint_bars:
    ax.barh(
        y=bar['y_pos'],
        width=bar['duration'],
        left=bar['start'],
        color=bar['color'],
        edgecolor=colors['bg_outer'], # Thin dark line between stints
        linewidth=1,
        height=0.65
    )
    
    # Add Compound Name in center of bar
    center_x = bar['start'] + (bar['duration'] / 2)
    ax.text(center_x, bar['y_pos'], bar['compound'], 
            ha='center', va='center', color=bar['text_color'], 
            fontsize=10, fontweight='bold')

# C. Draw specific "Lap X" markers on top of the lines
for marker in pit_stop_markers:
    # Using a bounding box (bbox) to create the label style from the image
    ax.text(marker['lap'], marker['y_pos'], f"Lap {int(marker['lap'])}",
            ha='center', va='center',
            color=colors['text_light'], fontsize=8, weight='bold',
            bbox=dict(facecolor=colors['marker_bg'], edgecolor='none', pad=3.5, alpha=1.0))


# --- 5. Final Formatting and Styling ---
# Set Y-axis labels (Drivers)
ax.set_yticks(range(len(driver_order)))
# Format labels like the image: "Name (P#)"
final_positions = {'VER': 'P1', 'PIA': 'P2', 'NOR': 'P3', 'LEC': 'P4'}
yticklabels = [f"{d} ({final_positions[d]})" for d in driver_order]
ax.set_yticklabels(yticklabels, color=colors['text_light'], fontsize=12)

# Set X-axis settings
ax.set_xlim(0, total_laps)
ax.set_xlabel("Lap Number", color=colors['text_light'], fontsize=12)
ax.tick_params(axis='x', colors=colors['text_light'], labelsize=10)

# Title
ax.set_title("2025 Abu Dhabi GP: Top 4 Tyre Strategies", color=colors['text_light'], fontsize=18, pad=20)

# Remove spines (the borders of the plot box)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color(colors['text_light'])

# Remove y-axis ticks marks but keep labels
ax.tick_params(axis='y', which='both', length=0)

plt.tight_layout()
plt.show()