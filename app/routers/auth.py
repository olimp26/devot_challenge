from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token
from app.crud.user import authenticate_user, create_user, get_user_by_email
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse

settings = get_settings()
router = APIRouter()


@router.post("/token", response_model=Token, summary="Login with email and password")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username
    password = form_data.password

    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, summary="Register new user with email, password and optional full name")
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
