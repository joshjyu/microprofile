from fastapi import FastAPI
from app.routers.profiles import router as profiles_router

app = FastAPI()
app.include_router(profiles_router)
