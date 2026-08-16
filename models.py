from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class WeightGoal(str, Enum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN = "maintain"
    GAIN_WEIGHT = "gain_weight"

class DietType(str, Enum):
    STANDARD = "standard"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    LACTOSE_FREE = "lactose_free"

# NOWE: Płeć i poziom aktywności fizycznej
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"

class UserProfileCreate(BaseModel):
    """Model validating incoming data from the Next.js frontend form."""
    age: int = Field(..., ge=16, le=120, description="Age in years")
    height_cm: float = Field(..., gt=100, le=250, description="Height in centimeters")
    weight_kg: float = Field(..., gt=30, le=300, description="Current weight in kilograms")
    gender: Gender = Field(..., description="Biological sex for BMR calculation")
    activity_level: ActivityLevel = Field(..., description="Daily activity level")
    
    goal: WeightGoal = Field(..., description="Main body weight goal")
    diet_type: DietType = Field(default=DietType.STANDARD, description="Preferred eating style")
    
    disliked_ingredients: List[str] = Field(
        default_factory=list, 
        description="List of ingredients to exclude (e.g., 'tomato', 'olives')"
    )

class UserProfileDB(UserProfileCreate):
    """Model saved in the database including calculated fields."""
    created_at: str
    
    # NOWE POŁA WYNIKOWE
    bmi: float
    bmr: int
    target_calories: int
    


class Meal(BaseModel):
    meal_type: str = Field(..., description="Typ posiłku: Śniadanie, Obiad, Przekąska, Kolacja")
    name: str = Field(..., description="Apetyczna nazwa posiłku")
    calories: int = Field(..., description="Kaloryczność posiłku")
    ingredients: List[str] = Field(..., description="Lista składników wraz z dokładną gramaturą, np. '100g kurczaka'")
    recipe: str = Field(..., description="Instrukcja przygotowania krok po kroku")

class DailyDietPlan(BaseModel):
    day_of_week: str = Field(..., description="Dzień tygodnia, np. Poniedziałek")
    meals: List[Meal] = Field(..., description="Lista zawierająca DOKŁADNIE 4 posiłki")


class DietGenerateRequest(BaseModel):
    diet_type_override: Optional[DietType] = Field(default=None)

class DietPlanDB(BaseModel):
    diet_id: str
    user_id: str
    created_at: str
    diet_type: DietType
    target_calories: int
    # ZMIANA Z 'str' NA NASZ STRUKTURYZOWANY MODEL:
    content: DailyDietPlan