from fastapi import FastAPI
from routers import profiles

app = FastAPI(title="AI Diet Backend API")

# Include all the separated routers here
app.include_router(profiles.router)

@app.get("/")
def root_endpoint():
    """Health check endpoint to ensure API is running."""
    return {"message": "API is fully operational"}