

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite3"
    DEBUG = True