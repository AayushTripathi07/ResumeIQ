from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import process

app = FastAPI(
    title="ResumeIQ API",
    description="Backend engine for AI-powered Resume optimization",
    version="1.0.0"
)

# Basic CORS config for local dev (React runs on 3000/3001)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(process.router, prefix="/api/process", tags=["Processing Engine"])

@app.get("/")
def health_check():
    return {"status": "success", "message": "ResumeIQ Backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
