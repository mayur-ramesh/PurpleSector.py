import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --- 1. Setup ---
plt.style.use('dark_background')

# --- 2. Data (Exact counts from reference) ---
#
data = [
    {'Driver': 'Bearman', 'Overtakes': 128, 'Team': 'Haas'},
    {'Driver': 'Albon', 'Overtakes': 118, 'Team': 'Williams'},
    {'Driver': 'Stroll', 'Overtakes': 109, 'Team': 'Aston Martin'},
    {'Driver': 'Hamilton', 'Overtakes': 107, 'Team': 'Ferrari'},
    {'Driver': 'Hulkenberg', 'Overtakes': 106, 'Team': 'Sauber'},
    {'Driver': 'Ocon', 'Overtakes': 105, 'Team': 'Haas'},
    {'Driver': 'Sainz', 'Overtakes': 100, 'Team': 'Williams'},
    {'Driver': 'Alonso', 'Overtakes': 97, 'Team': 'Aston Martin'},
    {'Driver': 'Antonelli', 'Overtakes': 94, 'Team': 'Mercedes'},
    {'Driver': 'Bortoleto', 'Overtakes': 89, 'Team': 'Sauber'},
    {'Driver': 'Tsunoda', 'Overtakes': 85, 'Team': 'Red Bull'},
    {'Driver': 'Gasly', 'Overtakes': 82, 'Team': 'Alpine'},
    {'Driver': 'Verstappen', 'Overtakes': 75, 'Team': 'Red Bull'},
    {'Driver': 'Hadjar', 'Overtakes': 72, 'Team': 'Racing Bulls'},
    {'Driver': 'Lawson', 'Overtakes': 70, 'Team': 'Racing Bulls'},
    {'Driver': 'Leclerc', 'Overtakes': 70, 'Team': 'Ferrari'},
    {'Driver': 'Russell', 'Overtakes': 66, 'Team': 'Mercedes'},
    {'Driver': 'Norris', 'Overtakes': 64, 'Team': 'McLaren'},
    {'Driver': 'Piastri', 'Overtakes': 56, 'Team': 'McLaren'},
    {'Driver': 'Colapinto', 'Overtakes': 37, 'Team': 'Alpine'},
    {'Driver': 'Doohan', 'Overtakes': 23, 'Team': 'Alpine'},
]

df = pd.DataFrame(data)

# --- 3. Plotting (Vertical Reel Format) ---
# Using a slightly wider aspect ratio to accommodate angled labels at the bottom
fig, ax = plt.subplots(figsize=(12, 18))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# Color Logic
colors = []
for d in df['Driver']:
    if d == 'Bearman': colors.append('#EF1C24')   # Haas Red (Hero)
    elif d in ['Norris', 'Piastri']: colors.append('#FF8700') # McLaren Orange
    else: colors.append('#333333')                # Background Grey

# Create VERTICAL Bar Chart (Swapped x and y)
sns.barplot(data=df, x='Driver', y='Overtakes', palette=colors, ax=ax, edgecolor='none')

# --- 4. Styling for Viral Impact ---
ax.set_title("MOST OVERTAKES OF 2025\n(THE FULL GRID)", 
             fontsize=24, fontweight='heavy', color='white', pad=30)

# Add Data Labels ABOVE the bars (Vertical orientation)
for i, row in df.iterrows():
    val = row['Overtakes']
    # Place text at x=i, y=val + offset. Rotate 90 deg for readability.
    ax.text(i, val + 5, str(val), ha='center', va='bottom', 
            color='white', fontweight='bold', fontsize=13, rotation=90)



# Clean up axes
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#333333')
ax.set_ylabel("")
ax.set_xlabel("")
# Hide Y-axis numbers
ax.set_yticks([]) 
# Rotate X-axis labels (Drivers) so they fit
ax.tick_params(axis='x', colors='white', labelsize=13, rotation=60)

plt.tight_layout()
# Adjust margins to fit tall labels at top and rotated labels at bottom
plt.subplots_adjust(top=0.88, bottom=0.12) 
plt.savefig('2025_Overtake_King_Vertical.png', dpi=300, facecolor='black')
plt.show()