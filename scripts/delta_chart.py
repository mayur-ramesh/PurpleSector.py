import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 1. Setup
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

# CONFIGURATION 
YEAR = 2025 
DRIVER_REF = 'VER'   # The Benchmark (Zero Line)
DRIVER_COMP = 'NOR'  # The Challenger (The Bars)

rounds = list(range(1, 25)) 
data = []

print(f"The Delta: Analyzing {DRIVER_REF} vs {DRIVER_COMP}...")
print("Checking for deepest common session (Q3 -> Q2 -> Q1) to ensure fair comparison...")

# Default colors
color_ref = '#808080'
color_comp = '#ffffff'

for r in rounds:
    try:
        session = fastf1.get_session(YEAR, r, 'Q')
        session.load(telemetry=False, weather=False)
        
        # Get Race Name for Labels
        race_name = session.event.EventName.replace(' Grand Prix', '').replace(' 2025', '')
        
        # Get Team Colors
        try:
            color_ref = fastf1.plotting.get_driver_color(DRIVER_REF, session=session)
            color_comp = fastf1.plotting.get_driver_color(DRIVER_COMP, session=session)
        except:
            pass # Keep defaults if color lookup fails
            
        # session.results contains the official Q1, Q2, Q3 times
        res = session.results
        
        # Check if drivers exist in this session
        if DRIVER_REF not in res['Abbreviation'].values or DRIVER_COMP not in res['Abbreviation'].values:
            print(f"Skipping R{r}: One or both drivers missing.")
            continue
            
        # Extract rows for both drivers
        d1_row = res.loc[res['Abbreviation'] == DRIVER_REF].iloc[0]
        d2_row = res.loc[res['Abbreviation'] == DRIVER_COMP].iloc[0]
        
        # LOGIC: Find Deepest Common Session
        # We prefer Q3, then Q2, then Q1. 
        # Both drivers must have a valid time (not NaT) in that session.
        
        t1, t2 = None, None
        session_used = "None"
        
        # Check Q3
        if not pd.isnull(d1_row['Q3']) and not pd.isnull(d2_row['Q3']):
            t1 = d1_row['Q3']
            t2 = d2_row['Q3']
            session_used = "Q3"
        # Check Q2
        elif not pd.isnull(d1_row['Q2']) and not pd.isnull(d2_row['Q2']):
            t1 = d1_row['Q2']
            t2 = d2_row['Q2']
            session_used = "Q2"
        # Check Q1
        elif not pd.isnull(d1_row['Q1']) and not pd.isnull(d2_row['Q1']):
            t1 = d1_row['Q1']
            t2 = d2_row['Q1']
            session_used = "Q1"
            
        # If no common time found (e.g. one crashed in Q1 without a time), skip
        if t1 is None or t2 is None:
            print(f"Skipping R{r}: No common valid time set.")
            continue
            
        # Calculate Gap in Seconds
        gap_seconds = t2.total_seconds() - t1.total_seconds()
        
        # Color Logic
        bar_color = color_comp if gap_seconds < 0 else color_ref
        
        data.append({
            'Round': r,
            'Race': race_name,
            'Gap_Sec': gap_seconds,
            'Color': bar_color,
            'Session': session_used
        })
        print(f"R{r} {race_name} ({session_used}): {gap_seconds:+.3f}s")
        
    except Exception as e:
        print(f"Error R{r}: {e}")

# 2. Create DataFrame
df = pd.DataFrame(data)

if df.empty:
    print("No data found. Check driver codes or year.")
    exit()

# 3. Plotting - FORCE DARK MODE
plt.style.use('dark_background') 
fig, ax = plt.subplots(figsize=(14, 8))

# FORCE Pitch Black Backgrounds
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# Draw the bars
bars = ax.bar(df['Round'], df['Gap_Sec'], color=df['Color'], edgecolor='white', linewidth=0.5)

# Add Trend Line
if len(df) > 1:
    z = np.polyfit(df['Round'], df['Gap_Sec'], 1)
    p = np.poly1d(z)
    ax.plot(df['Round'], p(df['Round']), "w--", linewidth=2, alpha=0.8, label='Trend')

# 4. Styling & Annotations
ax.axhline(0, color='white', linewidth=1, alpha=0.5)

# Titles
plt.suptitle(f"{YEAR} Qualifying Pace Gap (Seconds)", fontsize=14, y=0.93, color='#cccccc')

# Axis Labels
ax.set_ylabel(f"Gap (s) (Positive = {DRIVER_REF} Ahead)", fontsize=12, color='white')
ax.set_xlabel("Race Round", fontsize=12, color='white')

# X-Axis Ticks (R1\nBAH Format)
tick_labels = [f"R{row['Round']}\n{row['Race'][:3].upper()}" for i, row in df.iterrows()]
ax.set_xticks(df['Round'])
ax.set_xticklabels(tick_labels, fontsize=9, rotation=0, color='#dddddd')

# Legend
legend_patches = [
    mpatches.Patch(color=color_comp, label=f'{DRIVER_COMP} Faster'),
    mpatches.Patch(color=color_ref, label=f'{DRIVER_REF} Faster')
]
leg = ax.legend(handles=legend_patches, loc='upper right', frameon=True, facecolor='black', edgecolor='white')
for text in leg.get_texts():
    text.set_color("white")

# Bar Labels (Values)
for bar in bars:
    height = bar.get_height()
    label_y = height + 0.05 if height > 0 else height - 0.15
    if abs(height) > 2.0: label_y = height * 1.1 
    
    ax.text(bar.get_x() + bar.get_width()/2., label_y,
             f'{abs(height):.3f}s', 
             ha='center', va='center', 
             color='white', fontsize=7, fontweight='bold')

# Grid and Spines
ax.grid(axis='y', alpha=0.1, color='gray')
for spine in ax.spines.values():
    spine.set_color('white')
    spine.set_linewidth(0.5)

ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')

plt.tight_layout()
plt.show()