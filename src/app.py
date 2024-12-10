import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime
import threading
import time

from models import State, Ingredient, SetTemperature

app = fastapi.FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state = State()

def update_parameters_loop():
    while True:
        state.update_parameters()
        time.sleep(1)  # Update every second

# Start the parameter update loop in a separate thread
update_thread = threading.Thread(target=update_parameters_loop, daemon=True)
update_thread.start()

@app.get("/")
def index():
    return RedirectResponse(url="/static/index.html")

@app.get("/status", response_model=State)
def get_status():
    return state

@app.post("/add_ingredient")
def add_ingredient(ingredient: Ingredient):
    state.add_ingredient(ingredient)
    return state

@app.post("/flush")
def flush():
    global state
    state = State()
    return state

@app.post("/set_temperature")
def set_temperature(set_temperature: SetTemperature):
    state.temperature = set_temperature.temperature
    return state