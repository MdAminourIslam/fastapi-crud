from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal, engine
from models import Base, User

Base.metadata.create_all(bind=engine)

app = FastAPI()


# ========================
# SCHEMAS
# ========================
class UserCreate(BaseModel):
    name: str
    age: int


class UserResponse(BaseModel):
    id: int
    name: str
    age: int

    class Config:
        from_attributes = True


# ========================
# DB SESSION
# ========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========================
# CREATE
# ========================
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(name=user.name, age=user.age)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ========================
# READ
# ========================
@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# ========================
# UPDATE
# ========================
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name
    db_user.age = user.age

    db.commit()
    db.refresh(db_user)

    return db_user


# ========================
# DELETE
# ========================
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted"}