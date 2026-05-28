import os

def load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if not os.path.exists(env_file):
        return
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key = line.split('=', 1)[0].strip()
                value = line.split('=', 1)[1].strip()
                if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
                    value = value[1:-1]
                os.environ[key] = value

load_env()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    JWT_SECRET: str = os.getenv("PUBLIC_KEY_OR_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "hydra-iam"
    JWT_AUDIENCE: str = "internal-platforms"
    
    SMTP_HOST: str = os.getenv("MAIL_HOST", "smtp.office365.com")
    SMTP_PORT: int = int(os.getenv("MAIL_PORT", 587))
    SMTP_USER: str = os.getenv("MAIL_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    SMTP_FROM: str = os.getenv("MAIL_FROM_ADDRESS", "")
    SMTP_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Plataforma de Productividad")
    SMTP_USE_TLS: bool = os.getenv("MAIL_SECURE", "true").lower() == "true"

settings = Settings()