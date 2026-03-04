import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL") # type: ignore
    JWT_SECRET: str = "MISMO_SECRETO_QUE_USA_NESTJS"  # si usas HS256
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "hydra-iam"
    JWT_AUDIENCE: str = "internal-platforms"

settings = Settings()