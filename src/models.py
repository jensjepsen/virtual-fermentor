import pydantic
from collections import defaultdict

class Ingredient(pydantic.BaseModel):
    name: str
    milliliters: float

class State(pydantic.BaseModel):
    temperature: float = 20
    ingredients: dict[str, float] = defaultdict(float)
    percent_capacity: float = 0.0
    max_capacity: float = 10_000

    def add_ingredient(self, ingredient: Ingredient):
        self.ingredients[ingredient.name] += ingredient.milliliters
        self.percent_capacity = sum(self.ingredients.values()) / self.max_capacity * 100

class SetTemperature(pydantic.BaseModel):
    temperature: float