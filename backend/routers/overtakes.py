from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import fastf1
import pandas as pd

from analysis.overtakes import get_overtakes as _analyse_race
from config import DEFAULT_YEAR

router = APIRouter()


# ── Response models ───────────────────────────────────────────────────────────

class DriverRaceStats(BaseModel):
    driver_code: str
    full_name: str
    team: str
    color: str = '#888888'
    overtakes_made: int
    positions_gained_from_grid: int | None
    net_position_change: int | None


class RaceOvertakesResponse(BaseModel):
    year: int
    round: int
    session_name: str
    drivers: list[DriverRaceStats]


class DriverSeasonStats(BaseModel):
    driver_code: str
    full_name: str
    team: str
    color: str = '#888888'
    overtakes_made: int
    net_position_change: int | None
    rounds_counted: int


class SeasonOvertakesResponse(BaseModel):
    year: int
    rounds_completed: int
    drivers: list[DriverSeasonStats]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _completed_round_numbers(year: int) -> list[int]:
    """Return round numbers for every race that has already taken place."""
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    now = pd.Timestamp.now(tz="UTC")

    dates = pd.to_datetime(schedule["EventDate"], utc=True)
    completed = schedule[dates < now]
    return completed["RoundNumber"].dropna().astype(int).tolist()


def _aggregate_season(year: int) -> SeasonOvertakesResponse:
    round_numbers = _completed_round_numbers(year)

    # driver_code → running totals
    totals: dict[str, dict] = {}
    rounds_succeeded = 0

    for round_num in round_numbers:
        try:
            race_data = _analyse_race(year, round_num)
            rounds_succeeded += 1
        except Exception:
            # Session not yet published or data incomplete — skip silently
            continue

        for driver in race_data:
            code = driver["driver_code"]
            if code not in totals:
                totals[code] = {
                    "driver_code": code,
                    "full_name": driver["full_name"],
                    "team": driver["team"],
                    "color": driver.get("color", "#888888"),
                    "overtakes_made": 0,
                    "net_position_change_sum": 0,
                    "net_position_change_rounds": 0,
                    "rounds_counted": 0,
                }

            totals[code]["overtakes_made"] += driver["overtakes_made"]
            totals[code]["rounds_counted"] += 1

            npc = driver["net_position_change"]
            if npc is not None:
                totals[code]["net_position_change_sum"] += npc
                totals[code]["net_position_change_rounds"] += 1

    drivers: list[DriverSeasonStats] = []
    for entry in totals.values():
        npc = (
            entry["net_position_change_sum"]
            if entry["net_position_change_rounds"] > 0
            else None
        )
        drivers.append(
            DriverSeasonStats(
                driver_code=entry["driver_code"],
                full_name=entry["full_name"],
                team=entry["team"],
                color=entry["color"],
                overtakes_made=entry["overtakes_made"],
                net_position_change=npc,
                rounds_counted=entry["rounds_counted"],
            )
        )

    drivers.sort(key=lambda d: d.overtakes_made, reverse=True)

    return SeasonOvertakesResponse(
        year=year,
        rounds_completed=rounds_succeeded,
        drivers=drivers,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

# Declared before /{year} so FastAPI matches the bare slash correctly.
@router.get("/", response_model=SeasonOvertakesResponse, summary="Season leaderboard (default year)")
def get_default_season(
):
    """Season overtakes leaderboard for DEFAULT_YEAR."""
    try:
        return _aggregate_season(DEFAULT_YEAR)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{year}", response_model=SeasonOvertakesResponse, summary="Season leaderboard")
def get_season(year: int):
    """Cumulative overtakes leaderboard across all completed rounds in *year*."""
    try:
        return _aggregate_season(year)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{year}/{round_number}", response_model=RaceOvertakesResponse, summary="Single race")
def get_race(year: int, round_number: int):
    """Driver-level overtakes breakdown for a single race."""
    try:
        session = fastf1.get_session(year, round_number, 'R')
        session_name = session.event['EventName']
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not load session for year={year} round={round_number}: {exc}",
        )

    try:
        race_data = _analyse_race(year, round_number)
    except Exception:
        return JSONResponse(
            status_code=404,
            content={"error": "Data not available for this round yet"},
        )

    return RaceOvertakesResponse(
        year=year,
        round=round_number,
        session_name=session_name,
        drivers=[DriverRaceStats(**d) for d in race_data],
    )
