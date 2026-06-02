from fastapi import FastAPI
from app.database.database import engine, Base

app = FastAPI(
    title="NextChat API",
    description="Real-time team collaboration platform",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected successfully!")

@app.get("/")
async def root():
    return {"message": "Welcome to NextChat API"}