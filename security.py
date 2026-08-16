from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth

# Inicjalizacja aplikacji Firebase Admin
# Automatycznie pobierze poświadczenia z Twojego środowiska (lub chmury Cloud Run)
if not firebase_admin._apps:
    firebase_admin.initialize_app()

# Narzędzie FastAPI do wyciągania tokenu z nagłówka (Bearer Token)
security = HTTPBearer()

def verify_firebase_token(cred: HTTPAuthorizationCredentials = Depends(security)):
    """
    Funkcja przechwytuje Token JWT wysłany przez frontend (Next.js) 
    i sprawdza jego poprawność w Google Firebase.
    """
    token = cred.credentials
    
    try:
        # Weryfikacja tokenu - Google sprawdza podpis i datę ważności
        decoded_token = auth.verify_id_token(token)
        
        # Zwracamy zdekodowane dane (m.in. 'uid' użytkownika z Firebase)
        return decoded_token
        
    except Exception as e:
        # Jeśli token wygasł lub jest fałszywy, odrzucamy dostęp
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )