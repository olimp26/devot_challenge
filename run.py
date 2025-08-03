import os
import uvicorn
from dotenv import load_dotenv

from app.core.config import get_settings
from app.core.logger import Logger

load_dotenv()

settings = get_settings()

Logger.configure(settings.log_level)

os.makedirs("data", exist_ok=True)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        access_log=True
    )
