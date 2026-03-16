from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import fastf1
import fastf1.plotting
import math
import numpy as np
import pandas as pd

router = APIRouter()

class TelemetryRequest(BaseModel):
    year: int
    gp: str
    session_type: str
    driver1: str
    driver2: str


def safe_seconds(td) -> float | None:
    """Convert a Timedelta/NaT to float seconds, or None if NaT/null."""
    try:
        if td is None or (isinstance(td, float) and math.isnan(td)):
            return None
        if hasattr(td, 'total_seconds'):
            val = td.total_seconds()
            if math.isnan(val):
                return None
            return float(val)
        return float(td)
    except Exception:
        return None


def safe_float(x) -> float:
    """Convert a value to float, returning 0 for NaN/infinite/None."""
    try:
        v = float(x)
        return v if math.isfinite(v) else 0.0
    except Exception:
        return 0.0


@router.post("/")
def get_telemetry(req: TelemetryRequest):
    try:
        session = fastf1.get_session(req.year, req.gp, req.session_type)
        session.load()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load session: {str(e)}")

    driver_list = session.results['Abbreviation'].dropna().unique().tolist()
    if req.driver1 not in driver_list or req.driver2 not in driver_list:
        raise HTTPException(status_code=400, detail=f"Driver(s) not found. Available: {', '.join(driver_list)}")

    try:
        lap_d1 = session.laps.pick_driver(req.driver1).pick_fastest()
        lap_d2 = session.laps.pick_driver(req.driver2).pick_fastest()

        if lap_d1 is None or lap_d1.empty:
            raise ValueError(f"No laps found for {req.driver1}")
        if lap_d2 is None or lap_d2.empty:
            raise ValueError(f"No laps found for {req.driver2}")

        tel_d1 = lap_d1.get_car_data().add_distance()
        tel_d2 = lap_d2.get_car_data().add_distance()
        circuit_info = session.get_circuit_info()

        # Calculate Speed Delta (d1 vs d2, interpolated to d1 distance)
        d2_interp = np.interp(tel_d1['Distance'], tel_d2['Distance'], tel_d2['Speed'])
        delta = tel_d1['Speed'] - d2_interp

        # Serialize Circuit Info (Corners)
        corners = []
        if circuit_info is not None:
            for _, corner in circuit_info.corners.iterrows():
                corners.append({
                    "number": str(corner['Number']) + str(corner.get('Letter', '')),
                    "distance": safe_float(corner['Distance'])
                })

        # Get team colors safely
        try:
            color1 = fastf1.plotting.get_team_color(str(lap_d1['Team']), session=session)
        except Exception:
            color1 = '#9b59b6'
        try:
            color2 = fastf1.plotting.get_team_color(str(lap_d2['Team']), session=session)
        except Exception:
            color2 = '#888888'

        return {
            "driver1": {
                "name": req.driver1,
                "team": str(lap_d1['Team']),
                "color": color1,
                "sector1": safe_seconds(lap_d1['Sector1Time']),
                "sector2": safe_seconds(lap_d1['Sector2Time']),
                "sector3": safe_seconds(lap_d1['Sector3Time']),
                "lapTime": safe_seconds(lap_d1['LapTime']),
                "telemetry": {
                    "distance": [safe_float(x) for x in tel_d1['Distance']],
                    "speed": [safe_float(x) for x in tel_d1['Speed']],
                    "throttle": [safe_float(x) for x in tel_d1['Throttle']]
                }
            },
            "driver2": {
                "name": req.driver2,
                "team": str(lap_d2['Team']),
                "color": color2,
                "sector1": safe_seconds(lap_d2['Sector1Time']),
                "sector2": safe_seconds(lap_d2['Sector2Time']),
                "sector3": safe_seconds(lap_d2['Sector3Time']),
                "lapTime": safe_seconds(lap_d2['LapTime']),
                "telemetry": {
                    "distance": [safe_float(x) for x in tel_d2['Distance']],
                    "speed": [safe_float(x) for x in tel_d2['Speed']],
                    "throttle": [safe_float(x) for x in tel_d2['Throttle']]
                }
            },
            "delta": [safe_float(x) for x in delta],
            "corners": corners
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
