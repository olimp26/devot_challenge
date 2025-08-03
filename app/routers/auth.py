from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.exceptions import AuthExceptions, UserExceptions
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
        raise AuthExceptions.invalid_credentials()

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, summary="Register new user with email, password and optional full name")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise UserExceptions.email_already_registered()
    user = create_user(db, user_in)
    return user


@router.get("/me", response_model=UserResponse, summary="Get current user information")
def get_current_user_info(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user
