import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL") # type: ignore
    HYDRA_PUBLIC_KEY_URL: str = os.getenv("HYDRA_PUBLIC_KEY_URL") # type: ignore

settings = Settings()