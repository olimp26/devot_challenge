from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.exceptions import AuthExceptions, UserExceptions
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.deps import get_auth_service
from app.services.auth_service import AuthService

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token, summary="Login with email and password")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    email = form_data.username
    password = form_data.password

    user = auth_service.authenticate_user_credentials(email, password)
    if not user:
        raise AuthExceptions.invalid_credentials()

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, summary="Register new user with email, password and optional full name")
def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    existing_user = auth_service.get_user_by_email(user_in.email)
    if existing_user:
        raise UserExceptions.email_already_registered()
    user = auth_service.create_new_user(user_in)
    return user


@router.get("/me", response_model=UserResponse, summary="Get current user information")
def get_current_user_info(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user
