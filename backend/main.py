from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1
import os

from api import telemetry, delta, laps, tyres, overtakes, race_pace

# ─── CACHE SETUP ────────────────────────────────────────────────────────────
F1_CACHE_DIR = r"C:\Temp\f1_cache"
os.makedirs(F1_CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(F1_CACHE_DIR)

app = FastAPI(title="PurpleSector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])
app.include_router(delta.router, prefix="/api/delta", tags=["delta"])
app.include_router(laps.router, prefix="/api/laps", tags=["laps"])
app.include_router(tyres.router, prefix="/api/tyres", tags=["tyres"])
app.include_router(overtakes.router, prefix="/api/overtakes", tags=["overtakes"])
app.include_router(race_pace.router, prefix="/api/race_pace", tags=["race_pace"])

@app.get("/")
def read_root():
    return {"message": "PurpleSector API is running"}
