from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import router as health_router
from app.routes.resume_routes import router as resume_router
from app.routes.user_data_routes import router as user_data_router

app = FastAPI(
    title="ResuMatch AI Backend",
    description="API for AI-powered resume tailoring",
    version="0.1.0"
)

# --- CORS: allow Next dev server to connect ---
origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://127.0.0.1:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---
app.include_router(health_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(user_data_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "ResuMatch AI backend is running 🚀"}
