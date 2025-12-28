from pydantic import BaseModel
from typing import List, Dict, Optional

class Ingredient(BaseModel):
    name: str
    weight_g: float
    calories: float

class Meal(BaseModel):
    name: str
    ingredients: List[Ingredient] = []
    total_calories: float
    total_weight_g: float
    modifications: List[str] = []
    notes: Optional[str] = None

class NutritionResponse(BaseModel):
    meals: List[Meal]
    total_daily_calories: float
    message: str
    language: str = "auto"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    nutrition_data: Optional[NutritionResponse] = None
    session_id: str
