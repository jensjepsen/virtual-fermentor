import pydantic
from collections import defaultdict
import time
import math
from datetime import datetime

class Ingredient(pydantic.BaseModel):
    name: str
    milliliters: float

class State(pydantic.BaseModel):
    temperature: float = 20
    ingredients: dict[str, float] = defaultdict(float)
    percent_capacity: float = 0.0
    max_capacity: float = 10_000
    sugar_content: float = 0.0  # in Plato (°P)
    alcohol_content: float = 0.0  # in % ABV
    co2_content: float = 0.0  # in volumes of CO2
    cell_count: float = 0.0  # in millions cells/mL
    cell_viability: float = 0.0  # percentage of viable cells
    growth_rate: float = 0.0  # specific growth rate (per hour)
    generation_count: int = 0  # number of cell generations
    ph_level: float = 5.2  # typical starting pH for wort
    start_time: float = None
    is_fermenting: bool = False
    yeast_activity: float = 0.0  # percentage of yeast activity

    def add_ingredient(self, ingredient: Ingredient):
        self.ingredients[ingredient.name] += ingredient.milliliters
        self.percent_capacity = sum(self.ingredients.values()) / self.max_capacity * 100
        
        # If adding wort or malt, increase sugar content
        if any(term in ingredient.name.lower() for term in ['wort', 'malt', 'barley']):
            self.sugar_content += (ingredient.milliliters / self.max_capacity) * 12  # Assume max 12°P
        
        # If adding yeast, start fermentation
        if ingredient.name.lower() == 'yeast' and not self.is_fermenting:
            self.start_fermentation()
    
    def start_fermentation(self):
        self.is_fermenting = True
        self.start_time = time.time()
        self.yeast_activity = 100.0
        # Initialize cell stats when fermentation starts
        self.cell_count = 6.0  # Starting with 6 million cells/mL (typical pitching rate)
        self.cell_viability = 98.0  # Starting with fresh, healthy yeast
        self.growth_rate = 0.15  # Initial growth rate
        self.generation_count = 0
    
    def update_parameters(self):
        if not self.is_fermenting or self.start_time is None:
            return

        elapsed_hours = (time.time() - self.start_time) * 1  # Simulate 1 hour per second for better control
        
        # Temperature affects fermentation rate
        temp_factor = math.exp((self.temperature - 20) / 20)  # 20°C is optimal
        
        # Fermentation simulation
        # Sugar to alcohol conversion (simplified model)
        if self.sugar_content > 0:
            # Conversion rate depends on temperature and remaining sugar
            conversion_rate = 0.3 * temp_factor * (self.sugar_content / 12) * (self.yeast_activity / 100) * (self.cell_count / 100)
            sugar_converted = min(conversion_rate, self.sugar_content)
            
            self.sugar_content -= sugar_converted
            # Roughly 2:1 ratio of sugar to alcohol conversion
            self.alcohol_content += sugar_converted * 0.5
            
            # CO2 production correlates with fermentation rate
            self.co2_content += sugar_converted * 0.4  # CO2 production slightly higher than alcohol
            
            # pH decreases during fermentation
            self.ph_level = max(3.8, self.ph_level - (sugar_converted * 0.02))  # Slower pH change
            
            # Yeast activity decreases over time and with alcohol content
            alcohol_stress = self.alcohol_content * 3  # Alcohol stress factor
            time_stress = elapsed_hours / 4  # Time-based stress factor
            self.yeast_activity = max(0, 100 - time_stress - alcohol_stress)
            
            # Update cell statistics
            # Growth rate affected by temperature, sugar availability, and alcohol stress
            sugar_factor = self.sugar_content / 12  # Sugar availability factor
            alcohol_inhibition = max(0, 1 - (self.alcohol_content / 10))  # Alcohol inhibition
            self.growth_rate = 0.12 * temp_factor * sugar_factor * alcohol_inhibition * (self.cell_viability / 100)
            
            # Cell count increases based on growth rate, ensuring we start with initial cells
            if self.growth_rate > 0 and self.cell_count < 0.1:  # If cells were reset
                self.cell_count = 6.0  # Restore initial cell count
            elif self.growth_rate > 0:
                # Logistic growth model with carrying capacity
                carrying_capacity = 150.0  # Maximum sustainable cell density
                growth_factor = 1 - (self.cell_count / carrying_capacity)
                new_cells = self.cell_count * (self.growth_rate / 24) * growth_factor  # Hourly growth
                self.cell_count += new_cells
                
                # Update generation count when population doubles
                if self.cell_count >= self.cell_count * 1.8:  # 80% increase threshold
                    self.generation_count += 1
            
            # Cell viability is 0 if no cells, otherwise decreases with alcohol content and time
            if self.cell_count > 0:
                time_decay = elapsed_hours / 72  # Slower time-based decay
                alcohol_toxicity = self.alcohol_content / 15  # Reduced alcohol impact
                self.cell_viability = max(0, 98 - time_decay - alcohol_toxicity)
            
            # Adjust yeast activity based on cell viability
            self.yeast_activity *= (self.cell_viability / 100)
        
        # Ensure values stay within realistic ranges
        self.sugar_content = max(0, min(20, self.sugar_content))
        self.alcohol_content = max(0, min(12, self.alcohol_content))
        self.co2_content = max(0, min(4, self.co2_content))
        self.ph_level = max(3.8, min(5.5, self.ph_level))
        self.yeast_activity = max(0, min(100, self.yeast_activity))
        self.cell_viability = max(0, min(98, self.cell_viability))  # Max viability capped at initial 98%
        self.cell_viability = max(0, min(100, self.cell_viability))
        self.growth_rate = max(0, min(0.3, self.growth_rate))  # Max growth rate of 0.3/hour

class SetTemperature(pydantic.BaseModel):
    temperature: float