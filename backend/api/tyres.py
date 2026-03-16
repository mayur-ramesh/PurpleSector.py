from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import fastf1
import numpy as np

router = APIRouter()

class TyresRequest(BaseModel):
    year: int
    gp: str
    session_type: str

@router.post("/")
def get_tyres(req: TyresRequest):
    try:
        session = fastf1.get_session(req.year, req.gp, req.session_type)
        session.load(telemetry=False, weather=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load session: {str(e)}")

    colors = {
        'MEDIUM': '#ffd12b',
        'HARD': '#e0e0e0',
        'SOFT': '#ff3333',
        'INTERMEDIATE': '#39b54a',
        'WET': '#00aef0',
        'UNKNOWN': '#888888'
    }

    try:
        # Get Race Results order
        res = session.results
        driver_order = res['Abbreviation'].dropna().tolist()[:10] # Top 10 for neatness
        
        total_laps = session.total_laps
        stint_bars = []
        pit_stop_markers = []

        for i, driver in enumerate(driver_order):
            laps = session.laps.pick_driver(driver)
            if laps.empty: continue
            
            grouped_stints = laps.groupby('Stint')
            num_stints = grouped_stints.ngroups
            
            for stint_idx, (stint_num, stint_data) in enumerate(grouped_stints):
                compound = str(stint_data['Compound'].iloc[0])
                if compound == 'nan' or not compound: compound = 'UNKNOWN'
                
                start_lap = int(stint_data['LapNumber'].min())
                end_lap = int(stint_data['LapNumber'].max())
                
                visual_start = 0 if stint_idx == 0 else start_lap - 1
                duration = end_lap - visual_start
                
                stint_bars.append({
                    'yPos': i,
                    'driver': driver,
                    'compound': compound,
                    'start': visual_start,
                    'duration': duration,
                    'color': colors.get(str(compound).upper(), colors['UNKNOWN'])
                })
                
                if stint_idx < num_stints - 1:
                    pit_stop_markers.append({
                        'yPos': i,
                        'lap': end_lap,
                        'driver': driver
                    })

        return {
            "drivers": driver_order,
            "stints": stint_bars,
            "pitStops": pit_stop_markers,
            "totalLaps": int(total_laps) if total_laps else 50,
            "sessionName": f"{session.event['EventName']} {req.year} - Tyre Strategies"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
