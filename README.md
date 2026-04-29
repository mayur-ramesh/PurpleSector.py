# PurpleSector.py

An interactive F1 analytics web app — explore telemetry, qualifying gaps, tyre strategies, and race pace for any season using live FastF1 data.

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/mayur-ramesh/PurpleSector.py.git
cd PurpleSector.py
```

### 2. Backend setup

```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the API server
cd backend
uvicorn main:app --host 127.0.0.1 --port 8008 --reload
```

The API will be available at **http://localhost:8008**.

### 3. Frontend setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at **http://localhost:5173**.

> **Tip:** You can also run both servers together from the repo root with `python app.py`.

---

## Environment Variables

Copy `.env.example` to `.env` in the repo root and adjust as needed:

```bash
cp .env.example .env
```

See [.env.example](.env.example) for all available variables and their defaults. Currently the backend reads `BACKEND_HOST`, `BACKEND_PORT`, and `FASTF1_CACHE_DIR`; everything else falls back to a sensible default.

---

## Features

| Page | Description |
|------|-------------|
| **Qualifying Battle** | Side-by-side speed trace, throttle trace, and speed delta for any two drivers on their fastest lap. Includes sector gap cards and corner annotations. |
| **The Delta** | Bar chart of the qualifying time gap between two drivers across every round of a season, with a polynomial trend line overlay. |
| **Lap Ladder** | All drivers ranked by personal best lap time for a given session, with gap-to-P1 bars coloured by team. |
| **Tyre Strategy** | Visualises pit stop timing and compound stints for the top 10 finishers across the full race distance. |
| **Race Pace** | Compares clean-air race pace for up to three drivers lap-by-lap, with safety-car and outlier laps filtered out and a moving-average trend line. |
| **Overtakes** | Leaderboard of overtakes made per driver across the current season. |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data | [FastF1](https://theoehrly.github.io/Fast-F1/) |
| Backend | [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), Pandas, NumPy |
| Frontend | [React 19](https://react.dev/), [Vite](https://vitejs.dev/), [Recharts](https://recharts.org/) |

---

## Data Disclaimer

All data is sourced from the FastF1 library, which pulls from the official F1 timing API. This project is a fan-made tool and is not affiliated with Formula 1, the FIA, or any team.
