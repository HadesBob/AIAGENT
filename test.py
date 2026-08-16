import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
klucz = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=klucz)

# 1. Bezlitosna instrukcja systemowa
cyniczny_prompt = """
Jesteś zgryźliwym, wybitnie cynicznym i bezlitosnym felietonistą. 
Nie znosisz pseudonauki, internetowych guru i modnych trendów. 
Twój styl jest jadowity, pełen mrocznego sarkazmu i celnych, bolesnych porównań. 
Nie używaj grzecznościowych sformułowań ani sztucznej dyplomacji. Uderzaj w punkt.
Używaj bardzo ironicznych i sarkastycznych porównań. Opisz dietę karniwora jako debilizm.
Porównaj mity jakie głoszą propagatorzy diety karniwora i porównj je z faktami naukowymi z badań naukowych metaanaliz.
Nie zmyślaj faktów naukowych dla kontekstu.
"""

print("Czekam na felieton... (trzymaj się mocno)\n")

# 2. Wywołanie bez wymuszania JSON-a
odpowiedz = client.models.generate_content(
    model='gemini-3.7-flash',
    contents='Napisz bardzo cyniczny, prześmiewczy i bezlitosny tekst na temat internetowych "alfa samców" i ekspertów z Instagrama, którzy promują dietę carnivore (jedzenie samego mięsa i soli).',
    config=types.GenerateContentConfig(
        # Wstrzykujemy instrukcję
        system_instruction=cyniczny_prompt,
        
        # Zwiększamy temperaturę dla maksymalnej kreatywności w doborze słów
        temperature=2.0, 
        
        # Całkowicie wyłączamy filtry "nękania" (Harassment) 
        # i "niebezpiecznych treści" (Dangerous Content), aby model nie bał się kpić.
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            )
        ]
    )
)

print(odpowiedz.text)