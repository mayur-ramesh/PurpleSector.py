from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1
from pathlib import Path
import os

from api import telemetry, delta, laps, tyres, race_pace
from routers import overtakes

# ─── CACHE SETUP ────────────────────────────────────────────────────────────
_cache_env = os.getenv("FASTF1_CACHE_DIR")
F1_CACHE_DIR = Path(_cache_env).expanduser() if _cache_env else Path.home() / ".fastf1_cache"
F1_CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(F1_CACHE_DIR)

# ─── CORS ────────────────────────────────────────────────────────────────────
# Set ALLOWED_ORIGINS to a comma-separated list of frontend domains in production,
# e.g. "https://purplesector.up.railway.app,https://www.purplesector.app"
# Defaults to wildcard for local development.
_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if _origins_env:
    allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    allowed_origins = ["*"]

# Starlette forbids allow_credentials=True with a wildcard origin.
allow_credentials = allowed_origins != ["*"]

app = FastAPI(title="PurpleSector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
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
