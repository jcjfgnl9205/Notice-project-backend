import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    DB_USERNAME: str = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", 3306)
    DB_DATABASE: str = os.getenv("DB_DATABASE")
    DB_NAME: str = os.getenv("DB_NAME")

    DATABASE_URL = '{}://{}:{}@{}:{}/{}'.format(DB_DATABASE, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

settings = Settings()
