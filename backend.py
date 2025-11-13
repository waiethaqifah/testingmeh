# backend.py
from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

class Coordinates(BaseModel):
    lat: float
    lon: float

COORD_FILE = "coords.json"

@app.post("/save_coords")
def save_coords(coords: Coordinates):
    data = {"lat": coords.lat, "lon": coords.lon}
    with open(COORD_FILE, "w") as f:
        json.dump(data, f)
    return {"status": "success", "coords": data}

@app.get("/get_coords")
def get_coords():
    try:
        with open(COORD_FILE, "r") as f:
            data = json.load(f)
        return data
    except Exception:
        return {"lat": 0.0, "lon": 0.0}
