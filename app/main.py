from fastapi import FastAPI

from app.routers import auth_router, categories_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(categories_router, prefix="/categories",
                   tags=["categories"])
