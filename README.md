# 🟣 PurpleSector — F1 Qualifying Analysis

> A multi-page interactive website for deep F1 qualifying analysis — telemetry battles, season-long qualifying gaps, and lap time ladders. Built with **FastF1** and **Streamlit**.

---

## 📁 Project Structure

```
PurpleSector/           ← Streamlit web app
├── app.py              ← Main entry point (3-page app)
├── requirements.txt    ← Python dependencies
└── .streamlit/
    └── config.toml     ← Server config

scripts/                ← Standalone analysis scripts
├── quali_analysis.py   ← Pole battle telemetry (matplotlib)
├── delta_chart.py      ← Season-long qualifying gap bar chart
├── tyre_analysis.py    ← Tyre strategy analysis
├── overtakes.py        ← Overtake statistics
├── lap_times.py        ← Lap time totals
└── f1_insight_insta.py ← Instagram-format insight graphics

assets/                 ← Generated charts and images
```

---

## 🖥️ PurpleSector Web App

### Pages

| Page | Description |
|------|-------------|
| 🏎️ **Qualifying Battle** | Speed, throttle & delta traces for any two drivers on their fastest lap. Sector gap metrics + corner annotations. |
| 📊 **The Delta** | Season-long qualifying gap bar chart between two drivers. Uses deepest common session (Q3 → Q2 → Q1). Purple trend line overlay. |
| ⏱️ **Lap Time Ladder** | All drivers ranked by personal best lap time, coloured by team. |

### Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/mayur-ramesh/The-Project.git
cd The-Project

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r PurpleSector/requirements.txt

# 4. Run the app
# Important: use a local data dir to avoid OneDrive/network drive I/O issues
$env:STREAMLIT_DATA_DIR="C:\Temp\streamlit_data"   # Windows PowerShell
streamlit run PurpleSector/app.py
```

Open **http://localhost:8501** in your browser.

> **Note on caching:** FastF1 session data is cached at `C:\Temp\f1_cache` by default. The first load of any session will take ~30–60 seconds while data downloads. Subsequent loads are instant.

---

## 📜 Standalone Scripts

Each script in `scripts/` can be run independently. Configure the `YEAR`, `DRIVER_REF`, `DRIVER_COMP` variables at the top of each file.

```bash
python scripts/delta_chart.py
python scripts/quali_analysis.py
```

---

## 🛠️ Tech Stack

- **[FastF1](https://theoehrly.github.io/Fast-F1/)** — F1 timing & telemetry data
- **[Streamlit](https://streamlit.io/)** — interactive web UI
- **Matplotlib** — all charting
- **NumPy / Pandas** — data processing

---

## ⚠️ Data Disclaimer

All data is sourced from the FastF1 library, which pulls from the official F1 timing API. This project is a fan-made tool and is not affiliated with Formula 1, the FIA, or any team.
