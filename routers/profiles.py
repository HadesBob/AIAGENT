import uuid

from fastapi import APIRouter, Depends, HTTPException
from models import DietGenerateRequest, DietPlanDB, UserProfileCreate, UserProfileDB
from database import db
from datetime import datetime, timezone
from security import verify_firebase_token
from services.diet_service import calculate_bmi, calculate_target_calories, generate_diet_plan

router = APIRouter(
    prefix="/api/profiles",
    tags=["Profiles"]
)

@router.post("", response_model=UserProfileDB)
def create_profile(profile: UserProfileCreate, user_data: dict = Depends(verify_firebase_token)):
    # 1. Wyliczenia BMR i BMI (bez wywoływania Gemini!)
    bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
    bmr, target_calories = calculate_target_calories(profile)
    
    # 2. Zapis do bazy
    profile_to_save = UserProfileDB(
        **profile.model_dump(),
        bmi=bmi,
        bmr=bmr,
        target_calories=target_calories,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    db.collection("users").document(user_data["uid"]).set(profile_to_save.model_dump())
    
    # 3. Zwracamy gotowy profil do Next.js
    return profile_to_save



@router.get("/{firebase_uid}", response_model=UserProfileDB)
def get_profile(
    firebase_uid: str,
    # Zabezpieczamy również pobieranie
    user_data: dict = Depends(verify_firebase_token)
):
    """
    Fetches a user profile from Google Firestore by their Firebase UID.
    """
    if firebase_uid != user_data["uid"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    doc_ref = db.collection("users").document(firebase_uid)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return doc.to_dict()

@router.post("/diets", response_model=DietPlanDB)
def generate_new_diet(request: DietGenerateRequest, user_data: dict = Depends(verify_firebase_token)):
    firebase_uid = user_data["uid"]
    
    # 1. Pobieramy profil, żeby wiedzieć dla kogo generujemy
    doc = db.collection("users").document(firebase_uid).get()
    profile = UserProfileDB(**doc.to_dict())
    
    # 2. Gemini myśli (to potrwa kilka sekund)
    chosen_type = request.diet_type_override or profile.diet_type
    structured_diet_plan = generate_diet_plan(profile, chosen_type)
    
    # 3. Zapis i zwrot gotowej diety
    diet_id = str(uuid.uuid4())
    diet_plan = DietPlanDB(
        diet_id=diet_id,
        user_id=firebase_uid,
        created_at=datetime.now(timezone.utc).isoformat(),
        diet_type=chosen_type,
        target_calories=profile.target_calories,
        content=structured_diet_plan
    )
    
    db.collection("users").document(firebase_uid).collection("diets").document(diet_id).set(diet_plan.model_dump())
    return diet_plan

@router.get("/diets", response_model=list[DietPlanDB])
def get_user_diets(user_data: dict = Depends(verify_firebase_token)):
    """Pobiera pełną historię wygenerowanych diet dla zalogowanego użytkownika."""
    firebase_uid = user_data["uid"]
    
    # Odpytujemy podkolekcję 'diets' danego użytkownika
    diets_ref = db.collection("users").document(firebase_uid).collection("diets")
    
    # Sortujemy od najnowszej
    docs = diets_ref.order_by("created_at", direction="DESCENDING").stream()
    
    history = [doc.to_dict() for doc in docs]
    return history