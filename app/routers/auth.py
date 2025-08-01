from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/login")
def login():
    # TODO: Implement authentication endpoint
    raise HTTPException(
        status_code=501, detail="Login not implemented yet")


@router.post("/register")
def register():
    # TODO: Implement registration endpoint
    raise HTTPException(
        status_code=501, detail="Registration not implemented yet")


@router.get("/me")
def get_current_user():
    # TODO: Implement get current user endpoint
    raise HTTPException(
        status_code=501, detail="Get current user not implemented yet")
