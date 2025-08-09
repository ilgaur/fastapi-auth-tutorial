from fastapi import FastAPI
import uvicorn
from datetime import datetime

# Create our FastAPI app
app = FastAPI(title="Auth Tutorial", version="1.0.0")

@app.get("/health")
def health_check():
    """Simple health check to verify our API is running"""
    current_time = datetime.now().isoformat()
    print(f"🏥 Health check called at {current_time}")
    
    return {
        "status": "healthy",
        "timestamp": current_time,
        "message": "FastAPI Auth Tutorial is running!"
    }

if __name__ == "__main__":
    print("🚀 Starting FastAPI Auth Tutorial...")
    print("📍 Health endpoint: http://localhost:8000/health")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)