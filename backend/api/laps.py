from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import fastf1
import fastf1.plotting
import pandas as pd
import math

router = APIRouter()

class LapsRequest(BaseModel):
    year: int
    gp: str
    session_type: str


def format_laptime(seconds: float) -> str:
    """Format seconds to M:SS.mmm string."""
    try:
        if seconds is None or math.isnan(seconds):
            return "N/A"
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m}:{s:06.3f}"
    except Exception:
        return "N/A"


@router.post("/")
def get_lap_ladder(req: LapsRequest):
    try:
        session = fastf1.get_session(req.year, req.gp, req.session_type)
        session.load()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load session: {str(e)}")

    try:
        laps = session.laps.copy()
        laps = laps[laps['LapTime'].notna()]

        if laps.empty:
            raise HTTPException(status_code=404, detail="No lap time data found for this session.")

        best = (laps.groupby('Driver')['LapTime']
                    .min()
                    .reset_index()
                    .sort_values('LapTime'))

        best['LapTime_s'] = best['LapTime'].dt.total_seconds()
        best['Gap_to_P1'] = best['LapTime_s'] - best['LapTime_s'].iloc[0]

        driver_team = (laps.dropna(subset=['Team'])
                           .groupby('Driver')['Team']
                           .first()
                           .to_dict())

        best_data = []
        for idx, row in best.iterrows():
            team = driver_team.get(row['Driver'], 'Unknown')
            color = "#888888"
            try:
                color = fastf1.plotting.get_team_color(team, session=session)
            except Exception:
                pass

            lap_s = float(row['LapTime_s'])
            gap_s = float(row['Gap_to_P1'])

            best_data.append({
                "driver": row['Driver'],
                "team": team,
                "lapTimeS": lap_s,
                "lapTimeFormatted": format_laptime(lap_s),
                "gapToP1": gap_s,
                "color": color
            })

        return {
            "laps": best_data,
            "sessionName": f"{session.event['EventName']} {req.year} — {req.session_type}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
