from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PIAIC71-Hackathon1-v1 Backend API",
    description="Backend service for the PIAIC71 Hackathon project",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the PIAIC71-Hackathon1-v1 Backend API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend service is running"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "localhost")
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host=host, port=port)