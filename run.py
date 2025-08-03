import logging
from app.logger import Logger, LogLevels
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

Logger.configure(os.getenv("LOG_LEVEL", LogLevels.INFO))

os.makedirs("data", exist_ok=True)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    access_log = os.getenv("ACCESS_LOG", "true").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        access_log=access_log
    )
