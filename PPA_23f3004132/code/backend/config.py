import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "dev-salt")
    SECURITY_PASSWORD_HASH = "argon2"

    MAIL_HOST = os.environ.get("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_FROM = os.environ.get("MAIL_FROM", os.environ.get("MAIL_USERNAME", "noreply@ppa.com"))

    DAILY_REMINDER_HOUR = int(os.environ.get("DAILY_REMINDER_HOUR", 8))
    DAILY_REMINDER_MINUTE = int(os.environ.get("DAILY_REMINDER_MINUTE", 0))
    MONTHLY_REPORT_HOUR = int(os.environ.get("MONTHLY_REPORT_HOUR", 9))
    MONTHLY_REPORT_MINUTE = int(os.environ.get("MONTHLY_REPORT_MINUTE", 0))

    CACHE_TYPE = os.environ.get("CACHE_TYPE", "RedisCache")
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/2")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300))
