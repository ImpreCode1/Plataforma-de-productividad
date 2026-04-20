import os
from dotenv import load_dotenv

load_dotenv()

print(f"🔍 .env loaded, JWT_SECRET from env: {os.getenv('PUBLIC_KEY_OR_SECRET')}")

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL") #type: ignore
    JWT_SECRET: str = os.getenv("PUBLIC_KEY_OR_SECRET") #type: ignore
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "hydra-iam"
    JWT_AUDIENCE: str = "internal-platforms"

settings = Settings()
print(f"🔍 settings.JWT_SECRET: {settings.JWT_SECRET}")