import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

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