from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import UserCreate, UserResponse
from app.crud import get_user_by_email, create_user
from app.db import get_db

router = APIRouter()


@router.post("/login")
def login():
    # TODO: Implement authentication endpoint
    raise HTTPException(
        status_code=501, detail="Login not implemented yet")


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = create_user(db, user_in)
    return user


@router.get("/me")
def get_current_user():
    # TODO: Implement get current user endpoint
    raise HTTPException(
        status_code=501, detail="Get current user not implemented yet")
