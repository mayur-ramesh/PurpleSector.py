import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Setup
fastf1.Cache.enable_cache('cache')
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

# Configuration
TEST_YEAR = 2026
TEST_NUMBER = 1
DAYS_TO_ANALYZE = [1, 2, 3] # Adjust this list if Day 3 hasn't happened yet!

# Master storage
all_laps = []
team_laps_counter = {}

print(f"--- STARTING ANALYSIS FOR TEST {TEST_NUMBER} ---")

# 2. Loop through each day and gather data
for day in DAYS_TO_ANALYZE:
    print(f"Loading Day {day}...")
    try:
        session = fastf1.get_testing_session(TEST_YEAR, TEST_NUMBER, day)
        session.load(telemetry=False) # Laps only to save time
        
        # A. Count Laps for Reliability
        # We count every valid lap (even slow ones) for reliability stats
        counts = session.laps.groupby('Team')['LapNumber'].count()
        for team, count in counts.items():
            team_laps_counter[team] = team_laps_counter.get(team, 0) + count
            
        # B. Get Fastest Lap per Driver for this Day
        drivers = session.drivers
        for drv in drivers:
            try:
                # Get their fastest lap of the day
                fastest = session.laps.pick_driver(drv).pick_fastest()
                
                # Check if it exists (sometimes drivers don't set a time)
                if pd.notna(fastest['LapTime']):
                    all_laps.append({
                        'Day': day,
                        'Driver': drv,
                        'Team': fastest['Team'],
                        'LapTime': fastest['LapTime'].total_seconds(),
                        'Compound': fastest['Compound'] # Note: Might be 'TEST_UNKNOWN'
                    })
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ Could not load Day {day}: {e}")

# 3. Process Data
# Convert to DataFrame
df = pd.DataFrame(all_laps)

# Find the SINGLE fastest lap for each driver across ALL days
best_laps = df.loc[df.groupby("Driver")["LapTime"].idxmin()]
best_laps = best_laps.sort_values(by='LapTime')

# Prepare Reliability Data
df_reliability = pd.DataFrame(list(team_laps_counter.items()), columns=['Team', 'TotalLaps'])
df_reliability = df_reliability.sort_values('TotalLaps', ascending=False)

# -------------------------------
# VISUALIZATION 1: The Pace vs. Reliability Matrix
# -------------------------------
fig, ax = plt.subplots(figsize=(12, 8))

# Merge reliability into the pace dataframe for plotting
plot_data = pd.merge(best_laps, df_reliability, on='Team')

sns.scatterplot(
    data=plot_data, 
    x='TotalLaps', 
    y='LapTime', 
    hue='Team', 
    palette=fastf1.plotting.get_team_color_dict(session),
    s=300, 
    edgecolor='black',
    ax=ax
)

# Add Labels
for i, row in plot_data.iterrows():
    ax.text(row['TotalLaps'], row['LapTime'] - 0.05, row['Driver'], 
            ha='center', fontsize=9, color='white', weight='bold')

ax.set_title(f"The Testing Matrix: Speed vs. Reliability (Test {TEST_NUMBER})", fontsize=16, fontname='Formula1')
ax.set_xlabel("Total Laps Completed (Reliability)")
ax.set_ylabel("Best Lap Time (Performance)")
ax.invert_yaxis() # Faster is higher up
ax.grid(True, linestyle='--', alpha=0.3)

plt.tight_layout()
plt.show()

# -------------------------------
# VISUALIZATION 2: The Reliability Championship
# -------------------------------
fig2, ax2 = plt.subplots(figsize=(12, 6))

bars = ax2.bar(df_reliability['Team'], df_reliability['TotalLaps'])

# Color bars by team
for i, bar in enumerate(bars):
    team_name = df_reliability.iloc[i]['Team']
    try:
        col = fastf1.plotting.get_team_color(team_name, session=session)
        bar.set_color(col)
    except:
        bar.set_color('grey')

ax2.set_title(f"Distance Covered by Team (Test {TEST_NUMBER})", fontsize=16, fontname='Formula1')
ax2.set_ylabel("Total Laps")
ax2.bar_label(bars, padding=3, color='white', weight='bold')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# -------------------------------
# DATA PRINT OUT
# -------------------------------
print("\n--- OVERALL FASTEST TIMES (COMBINED DAYS) ---")
print(best_laps[['Driver', 'Team', 'Day', 'LapTime']].head(10).to_string(index=False))