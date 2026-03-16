from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import math

router = APIRouter()

class DeltaRequest(BaseModel):
    year: int
    ref_driver: str
    comp_driver: str

@router.post("/")
def get_delta(req: DeltaRequest):
    data = []
    rounds = list(range(1, 30))
    ref_color = '#808080'
    comp_color = '#ffffff'

    for r in rounds:
        try:
            s = fastf1.get_session(req.year, r, 'Q')
            s.load(telemetry=False, weather=False, messages=False)
            
            # Fetch colors
            try:
                ref_color = fastf1.plotting.get_driver_color(req.ref_driver, session=s)
                comp_color = fastf1.plotting.get_driver_color(req.comp_driver, session=s)
            except Exception:
                pass

            race_name = s.event.EventName.replace(' Grand Prix', '').replace(f' {req.year}', '')
            res = s.results

            if req.ref_driver not in res['Abbreviation'].values or req.comp_driver not in res['Abbreviation'].values:
                continue

            d1_row = res.loc[res['Abbreviation'] == req.ref_driver].iloc[0]
            d2_row = res.loc[res['Abbreviation'] == req.comp_driver].iloc[0]

            t1 = t2 = None
            session_used = "None"

            for seg in ['Q3', 'Q2', 'Q1']:
                if not pd.isnull(d1_row[seg]) and not pd.isnull(d2_row[seg]):
                    t1, t2 = d1_row[seg], d2_row[seg]
                    session_used = seg
                    break

            if t1 is None:
                continue

            gap = t2.total_seconds() - t1.total_seconds()
            data.append({
                'round': r,
                'race': race_name,
                'gap': float(gap),
                'color': comp_color if gap < 0 else ref_color,
                'seg': session_used
            })

        except Exception:
            # Round doesn't exist or no data
            pass
            
    if not data:
        raise HTTPException(status_code=404, detail="No common qualifying sessions found")
        
    df = pd.DataFrame(data)
    trendData = []
    
    if len(df) > 2:
        z = np.polyfit(range(len(df)), df['gap'], 1)
        p = np.poly1d(z)
        trendData = [float(x) for x in p(range(len(df)))]
        
    return {
        "bars": data,
        "trend": trendData,
        "ref_driver": req.ref_driver,
        "comp_driver": req.comp_driver
    }
