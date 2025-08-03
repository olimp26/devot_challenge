from fastapi import FastAPI

from app.routers import auth_router, categories_router, transactions_router, summary_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(transactions_router)
app.include_router(summary_router)
