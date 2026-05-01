import fastf1
import pandas as pd


def get_overtakes(year: int, round_number: int) -> list[dict]:
    """
    Detect on-track overtakes from lap-by-lap position changes for a race session.

    An overtake made is counted whenever a driver's position number decreases
    (improves) between two consecutive laps. If a driver jumps from P6 to P4,
    that counts as 2 overtakes made. Lap 1 is excluded entirely because grid
    spread is not racing action. Non-consecutive lap pairs (e.g. a lap is
    missing from the data) are also skipped to avoid false positives.
    """
    session = fastf1.get_session(year, round_number, 'R')
    session.load(telemetry=False, weather=False, messages=False)

    laps = session.laps[session.laps['LapNumber'] > 1].copy()
    results = session.results

    # ── Driver metadata from results ─────────────────────────────────────────
    driver_meta: dict[str, dict] = {}
    for _, row in results.iterrows():
        code = row.get('Abbreviation')
        if not code or pd.isna(code):
            continue

        grid = row.get('GridPosition')
        final = row.get('Position')

        try:
            grid_f = float(grid)
            grid_pos = int(grid_f) if not pd.isna(grid_f) else None
        except (TypeError, ValueError):
            grid_pos = None

        try:
            final_f = float(final)
            final_pos = int(final_f) if not pd.isna(final_f) else None
        except (TypeError, ValueError):
            final_pos = None

        raw_color = row.get('TeamColor')
        if raw_color and not pd.isna(raw_color):
            color = str(raw_color) if str(raw_color).startswith('#') else f"#{raw_color}"
        else:
            color = '#888888'

        driver_meta[code] = {
            'full_name': row.get('FullName') or code,
            'team': row.get('TeamName') or 'Unknown',
            'color': color,
            'grid_position': grid_pos,
            'final_position': final_pos,
        }

    # ── Per-driver overtake counting ──────────────────────────────────────────
    output: list[dict] = []

    for driver_code, driver_laps in laps.groupby('Driver'):
        driver_laps = driver_laps.sort_values('LapNumber').reset_index(drop=True)

        overtakes_made = 0
        prev_lap_num: int | None = None
        prev_position: float | None = None

        for _, row in driver_laps.iterrows():
            lap_num = row['LapNumber']
            position = row['Position']

            # Skip laps with missing position data
            if pd.isna(position):
                prev_lap_num = lap_num
                prev_position = None
                continue

            position = float(position)

            if prev_position is not None and lap_num == prev_lap_num + 1:
                delta = prev_position - position  # positive → gained positions
                if delta > 0:
                    overtakes_made += int(delta)

            prev_lap_num = lap_num
            prev_position = position

        # ── Summary metrics ───────────────────────────────────────────────────
        meta = driver_meta.get(driver_code, {})
        grid_pos = meta.get('grid_position')
        final_pos = meta.get('final_position')

        if grid_pos is not None and final_pos is not None:
            positions_gained_from_grid = grid_pos - final_pos
        else:
            positions_gained_from_grid = None

        # net_position_change: first valid lap-2+ position → last valid position
        valid_positions = driver_laps['Position'].dropna()
        if len(valid_positions) >= 2:
            net_position_change = int(
                float(valid_positions.iloc[0]) - float(valid_positions.iloc[-1])
            )
        else:
            net_position_change = None

        output.append({
            'driver_code': driver_code,
            'full_name': meta.get('full_name', driver_code),
            'team': meta.get('team', 'Unknown'),
            'color': meta.get('color', '#888888'),
            'overtakes_made': overtakes_made,
            'positions_gained_from_grid': positions_gained_from_grid,
            'net_position_change': net_position_change,
        })

    output.sort(key=lambda x: x['overtakes_made'], reverse=True)
    return output
