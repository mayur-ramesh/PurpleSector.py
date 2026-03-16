from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np

router = APIRouter()

class RacePaceRequest(BaseModel):
    year: int
    gp: str
    session_type: str = 'R'
    driver1: str
    driver2: str
    driver3: str = None

def filter_outliers(laps, margin=1.07):
    if laps.empty:
        return laps
    # Filter out in/out laps
    laps = laps.pick_quicklaps(margin)
    # Filter out safety car / VSC laps
    laps = laps.pick_track_status('1', how='any')
    return laps

def process_driver_laps(session, d_code):
    laps = session.laps.pick_driver(d_code)
    filtered = filter_outliers(laps)
    
    # Calculate rolling MA to show tyre degradation trend
    if not filtered.empty:
        filtered = filtered.copy()
        # Ensure lap times are strictly positive
        valid_laps = [t for t in filtered['LapTime'].dt.total_seconds() if pd.notna(t) and t > 0]
        if valid_laps:
            filtered.loc[:, 'LapTimeS'] = filtered['LapTime'].dt.total_seconds()
            
            # Simple moving average (window 3) for tyre deg trend
            filtered.loc[:, 'Trend'] = filtered['LapTimeS'].rolling(window=3, min_periods=1).mean()
        else:
             filtered.loc[:, 'LapTimeS'] = []
             filtered.loc[:, 'Trend'] = []
    
    # Safely get team color
    color = '#ffffff'
    if not laps.empty:
        try:
            team = str(laps.iloc[0]['Team'])
            color = fastf1.plotting.get_team_color(team, session=session)
        except Exception:
            pass

    return {
        "name": d_code,
        "color": color,
        "laps": filtered['LapNumber'].tolist() if not filtered.empty else [],
        "times": filtered['LapTimeS'].tolist() if not filtered.empty and 'LapTimeS' in filtered.columns else [],
        "trend": [0 if pd.isna(t) else t for t in filtered['Trend'].tolist()] if not filtered.empty and 'Trend' in filtered.columns else []
    }

@router.post("/")
def get_race_pace(req: RacePaceRequest):
    try:
        session = fastf1.get_session(req.year, req.gp, req.session_type)
        session.load(telemetry=False, weather=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load session: {str(e)}")

    driver_list = session.results['Abbreviation'].dropna().unique().tolist()
    d1_valid = req.driver1 in driver_list
    d2_valid = req.driver2 in driver_list
    d3_valid = req.driver3 in driver_list if req.driver3 else True
    
    if not (d1_valid and d2_valid and d3_valid):
        raise HTTPException(status_code=400, detail=f"Driver(s) not found. Available: {', '.join(driver_list)}")

    try:
        data = {
            "sessionName": f"{session.event['EventName']} {session.name} ({req.year})",
            "drivers": []
        }
        
        # Process drivers
        drivers = [req.driver1, req.driver2]
        if req.driver3:
            drivers.append(req.driver3)
            
        for d in drivers:
            data["drivers"].append(process_driver_laps(session, d))

        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
