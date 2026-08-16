import os

from pydantic import json
from models import DailyDietPlan, DietType, UserProfileCreate, UserProfileDB, WeightGoal, ActivityLevel, Gender
from google import genai
from google.genai import types

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def calculate_target_calories(profile: UserProfileCreate) -> tuple[int, int]:
    """Zwraca BMR oraz docelowe kalorie (TDEE +/- cel)."""
    # Wzór Mifflina-St Jeora na BMR
    bmr_base = (10 * profile.weight_kg) + (6.25 * profile.height_cm) - (5 * profile.age)
    
    if profile.gender == Gender.MALE:
        bmr = bmr_base + 5
    else:
        bmr = bmr_base - 161
        
    # Mnożnik aktywności (TDEE)
    activity_multipliers = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHT: 1.375,
        ActivityLevel.MODERATE: 1.55,
        ActivityLevel.ACTIVE: 1.725
    }
    tdee = bmr * activity_multipliers[profile.activity_level]
    
    # Modyfikacja na podstawie celu
    if profile.goal == WeightGoal.LOSE_WEIGHT:
        target_calories = tdee - 500  # Deficyt
    elif profile.goal == WeightGoal.GAIN_WEIGHT:
        target_calories = tdee + 500  # Nadwyżka
    else:
        target_calories = tdee        # Utrzymanie
        
    return int(bmr), int(target_calories)


def generate_diet_plan(profile: UserProfileDB, requested_diet_type: DietType) -> DailyDietPlan:
    """Generuje dietę i zwraca ustrukturyzowany obiekt zgodny z naszym układem."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    system_instruction = """
    Jesteś profesjonalnym dietetykiem. Twoim zadaniem jest ułożenie diety na jeden dzień.
    Musisz wygenerować DOKŁADNIE 4 posiłki: Śniadanie, Obiad, Przekąska, Kolacja.
    Suma kalorii z posiłków musi w przybliżeniu zgadzać się z zapotrzebowaniem.
    Zwróć tylko i wyłącznie poprawnego JSON-a zgodnego ze schematem.
    """
    
    prompt = f"""
    Cel: {profile.goal.value}
    Typ diety: {requested_diet_type.value}
    Zapotrzebowanie kaloryczne: {profile.target_calories} kcal
    Wykluczenia: {', '.join(profile.disliked_ingredients) if profile.disliked_ingredients else 'brak'}
    """
    
    response = client.models.generate_content(
        model='gemini-3.7-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            # Obniżamy temperaturę do 0.4 - chcemy konkretów matematycznych, a nie fantazji
            temperature=0.4, 
            # Dwa kluczowe parametry wymuszające układ:
            response_mime_type="application/json",
            response_schema=DailyDietPlan, 
        )
    )
    
    # Przetwarzamy tekstowego JSON-a od Gemini na prawdziwy obiekt Pythona (model Pydantic)
    try:
        plan_dict = json.loads(response.text)
        return DailyDietPlan(**plan_dict)
    except json.JSONDecodeError:
        raise ValueError("Model AI nie zwrócił poprawnego formatu danych.")