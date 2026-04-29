import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --- 1. Setup & Style ---
fastf1.Cache.enable_cache('cache')
bg_color = '#000000'
text_color = '#FFFFFF'
plt.style.use('dark_background')
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

# --- 2. Data Collection ---
schedule = fastf1.get_event_schedule(2025, include_testing=False)
races = schedule[schedule['RoundNumber'] > 0]

driver_laps = {}
total_season_laps = 0

print(f"Processing {len(races)} rounds for Reel format...")

for i, race in races.iterrows():
    try:
        session = fastf1.get_session(2025, race['RoundNumber'], 'R')
        session.load(laps=False, telemetry=False, weather=False, messages=False)
        
        results = session.results
        if results.empty: continue
            
        race_distance = results['Laps'].max()
        total_season_laps += race_distance
        
        for driver in results['Abbreviation']:
            laps_completed = results.loc[results['Abbreviation'] == driver, 'Laps'].values[0]
            if pd.isna(laps_completed): laps_completed = 0
            driver_laps[driver] = driver_laps.get(driver, 0) + laps_completed
                
    except Exception as e:
        print(f"Error R{race['RoundNumber']}: {e}")

# --- 3. Data Processing ---
df = pd.DataFrame(list(driver_laps.items()), columns=['Driver', 'TotalLaps'])
df = df.sort_values('TotalLaps', ascending=False).reset_index(drop=True)
df['Percent'] = (df['TotalLaps'] / total_season_laps) * 100

# --- 4. Plotting ---
fig, ax = plt.subplots(figsize=(10, 16))

fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

# Define Colors
rus_teal = '#00D2BE'
nor_orange = '#FF8700'
ver_blue = '#0600EF'
base_grey = '#333333'

palette = []
for driver in df['Driver']:
    if driver == 'RUS': palette.append(rus_teal)
    elif driver == 'NOR': palette.append(nor_orange)
    elif driver == 'VER': palette.append(ver_blue)
    else: palette.append(base_grey)

# Create VERTICAL bars
bars = sns.barplot(data=df, x='Driver', y='TotalLaps',
                   palette=palette, edgecolor=bg_color, linewidth=2)

# --- 5. Formatting ---
fig.text(0.5, 0.92, f"Total possible laps: {int(total_season_laps)}",
         ha='center', color=rus_teal, fontsize=16, fontweight='bold')

ax.set_xlabel("")
ax.set_ylabel("Laps Completed", fontsize=14, color=base_grey)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color(base_grey)

ax.tick_params(axis='x', colors=text_color, labelsize=14, rotation=45)
ax.set_yticks([])

ax.axhline(y=total_season_laps, color=text_color, linestyle='--', linewidth=1, alpha=0.5)

# --- 6. Add Data Labels ---
for i, row in df.iterrows():
    label_color = text_color
    weight = 'normal'
    if row['Driver'] == 'RUS': label_color = rus_teal; weight='bold'
    elif row['Driver'] == 'NOR': label_color = nor_orange; weight='bold'
    elif row['Driver'] == 'VER': label_color = ver_blue; weight='bold'
    elif row['TotalLaps'] < 500: label_color = base_grey

    label_text = f"{int(row['TotalLaps'])} ({row['Percent']:.1f}%)"
    
    ax.text(i, row['TotalLaps'] + 50,
            label_text,
            ha='center', va='bottom',
            color=label_color, fontweight=weight, fontsize=11,
            rotation=90)

# --- Key Fix for Cutoff Labels ---
# Increase bottom margin from 0.05 to 0.15 to give space for rotated labels
plt.tight_layout()
plt.subplots_adjust(top=0.78, bottom=0.15)

plt.savefig('2025_Reliability_Reel.png', dpi=300, facecolor=bg_color)
plt.show()