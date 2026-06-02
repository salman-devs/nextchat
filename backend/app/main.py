from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
from app.models import models
from app.routers import auth, workspaces

app = FastAPI(
    title="NextChat API",
    description="Real-time team collaboration platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("Database connected and tables created!")

app.include_router(auth.router)
app.include_router(workspaces.router)

@app.get("/")
async def root():
    return {"message": "Welcome to NextChat API"}