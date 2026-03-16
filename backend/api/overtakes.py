from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

@router.get("/")
def get_overtakes():
    # Hardcoded data for current season as requested
    data = [
        {'driver': 'Bearman', 'overtakes': 128, 'team': 'Haas', 'color': '#EF1C24'},
        {'driver': 'Albon', 'overtakes': 118, 'team': 'Williams', 'color': '#005aff'},
        {'driver': 'Stroll', 'overtakes': 109, 'team': 'Aston Martin', 'color': '#006F62'},
        {'driver': 'Hamilton', 'overtakes': 107, 'team': 'Ferrari', 'color': '#dc0000'},
        {'driver': 'Hulkenberg', 'overtakes': 106, 'team': 'Sauber', 'color': '#00e701'},
        {'driver': 'Ocon', 'overtakes': 105, 'team': 'Haas', 'color': '#EF1C24'},
        {'driver': 'Sainz', 'overtakes': 100, 'team': 'Williams', 'color': '#005aff'},
        {'driver': 'Alonso', 'overtakes': 97, 'team': 'Aston Martin', 'color': '#006F62'},
        {'driver': 'Antonelli', 'overtakes': 94, 'team': 'Mercedes', 'color': '#00d2be'},
        {'driver': 'Bortoleto', 'overtakes': 89, 'team': 'Sauber', 'color': '#00e701'},
        {'driver': 'Tsunoda', 'overtakes': 85, 'team': 'Red Bull', 'color': '#0600ef'},
        {'driver': 'Gasly', 'overtakes': 82, 'team': 'Alpine', 'color': '#0090ff'},
        {'driver': 'Verstappen', 'overtakes': 75, 'team': 'Red Bull', 'color': '#0600ef'},
        {'driver': 'Hadjar', 'overtakes': 72, 'team': 'Racing Bulls', 'color': '#2b4562'},
        {'driver': 'Lawson', 'overtakes': 70, 'team': 'Racing Bulls', 'color': '#2b4562'},
        {'driver': 'Leclerc', 'overtakes': 70, 'team': 'Ferrari', 'color': '#dc0000'},
        {'driver': 'Russell', 'overtakes': 66, 'team': 'Mercedes', 'color': '#00d2be'},
        {'driver': 'Norris', 'overtakes': 64, 'team': 'McLaren', 'color': '#FF8700'},
        {'driver': 'Piastri', 'overtakes': 56, 'team': 'McLaren', 'color': '#FF8700'},
        {'driver': 'Colapinto', 'overtakes': 37, 'team': 'Alpine', 'color': '#0090ff'},
        {'driver': 'Doohan', 'overtakes': 23, 'team': 'Alpine', 'color': '#0090ff'}
    ]
    return {"overtakes": data}
