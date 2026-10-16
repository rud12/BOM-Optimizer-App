from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router

from core.config import CORS_ORIGINS
from core.database import Base, engine


app = FastAPI(title="BOM Optimizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)