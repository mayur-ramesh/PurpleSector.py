import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
import os

# 1. SETUP (Cache Fix)
cache_dir = 'f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir) 

def create_insta_post(year, gp, session_type):
    # 2. VALIDATION (Data Check)
    if year < 2018:
        print("❌ Error: Telemetry is only available for 2018+.")
        return

    print(f"🚀 Creating Instagram Post for {gp} {year}...")
    
    # 3. DATA LOADING
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
    except Exception as e:
        print(f"Error: {e}")
        return

    # 4. DRIVER SELECTION
    fastest = session.laps.pick_fastest()
    d1 = fastest['Driver']
    d1_team = fastest['Team']
    
    # Find P2
    drivers = session.results
    d2 = drivers.iloc[1]['Abbreviation']
    p2_lap = session.laps.pick_driver(d2).pick_fastest()
    d2_team = p2_lap['Team']
    
    print(f"📸 Matchup: {d1} vs {d2}")

    # 5. TELEMETRY
    d1_tel = fastest.get_car_data().add_distance()
    d2_tel = p2_lap.get_car_data().add_distance()
    
    # Interpolation for Delta
    d2_speed_interp = np.interp(d1_tel['Distance'], d2_tel['Distance'], d2_tel['Speed'])
    delta = d1_tel['Speed'] - d2_speed_interp

    # 6. INSTAGRAM STYLING
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    
    # ASPECT RATIO: 10x12.5 inches = 4:5 Ratio (Perfect for IG)
    fig, ax = plt.subplots(3, 1, figsize=(10, 12.5), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # FONT SIZES (Bigger for mobile)
    plt.rcParams.update({'font.size': 14})
    
    c1 = fastf1.plotting.get_team_color(d1_team, session=session)
    c2 = fastf1.plotting.get_team_color(d2_team, session=session)
    
    # Plot Speed
    ax[0].plot(d1_tel['Distance'], d1_tel['Speed'], color=c1, label=d1, linewidth=3)
    ax[0].plot(d2_tel['Distance'], d2_tel['Speed'], color=c2, label=d2, linestyle='--', linewidth=3)
    ax[0].set_ylabel('Speed (km/h)', fontsize=16)
    ax[0].legend(loc='lower right', fontsize=14)
    ax[0].set_title(f"{d1} vs {d2}\n{session.event['EventName']} {year}", fontsize=20, fontweight='bold')

    # Plot Throttle
    ax[1].plot(d1_tel['Distance'], d1_tel['Throttle'], color=c1, linewidth=2)
    ax[1].plot(d2_tel['Distance'], d2_tel['Throttle'], color=c2, linestyle='--', linewidth=2)
    ax[1].set_ylabel('Throttle %', fontsize=16)
    ax[1].set_yticks([0, 100])

    # Plot Delta
    ax[2].plot(d1_tel['Distance'], delta, color='white', linewidth=1)
    ax[2].axhline(0, color='gray', linestyle='--', linewidth=1)
    ax[2].fill_between(d1_tel['Distance'], delta, 0, where=delta>0, facecolor=c1, alpha=0.5)
    ax[2].fill_between(d1_tel['Distance'], delta, 0, where=delta<0, facecolor=c2, alpha=0.5)
    ax[2].set_ylabel(f'Gap (km/h)\n(+{d1} Faster)', fontsize=14)
    ax[2].set_xlabel('Track Distance (m)', fontsize=16)

    plt.tight_layout()
    
    # SAVE FILE
    filename = "instagram_post.png"
    plt.savefig(filename, dpi=150) # High DPI for crisp text
    print(f"✅ Saved as {filename}")
    plt.show()

# Run it!
create_insta_post(2018, 'Spain', 'Q')