from fastapi import FastAPI

from app.database import engine, Base
from app.routes import user

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)