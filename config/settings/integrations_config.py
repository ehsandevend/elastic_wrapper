from decouple import config
from pathlib import Path
from shared.enums import EnvironmentChoices


BASE_DIR = Path(__file__).resolve().parent.parent.parent

if (
    config("ENVIRONMENT", cast=str, default=EnvironmentChoices.DEV).lower() == EnvironmentChoices.DEV
):
    from decouple import Config, RepositoryEnv

    DEV_ENV_FILE = ".app_envs/development/.env"
    config = Config(RepositoryEnv(DEV_ENV_FILE))


class BaseConfig:
    ENVIRONMENT = config("ENVIRONMENT", default=EnvironmentChoices.DEV).lower()
    ALLOWED_HOSTS = config(
        "ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")]
    )
    DEBUG = config("DEBUG", cast=bool, default=False)


    @classmethod
    def is_development(cls):
        return cls.ENVIRONMENT == EnvironmentChoices.DEV

    @classmethod
    def is_production(cls):
        return cls.ENVIRONMENT == EnvironmentChoices.PROD


class ELKConfig(BaseConfig):
    ELASTIC_READ_USER = config("ELASTIC_READ_USER", cast=str, default=None)
    ELASTIC_READ_PASSWORD = config("ELASTIC_READ_PASSWORD", cast=str, default=None)

    ELASTIC_WRITE_USER = config("ELASTIC_WRITE_USER", cast=str, default=None)
    ELASTIC_WRITE_PASSWORD = config("ELASTIC_WRITE_PASSWORD", cast=str, default=None)

    ELASTIC_HOST = config("ELASTIC_HOST", cast=str)
    ELASTIC_PORT = config("ELASTIC_PORT", cast=int, default=9200)

    ELASTIC_CONNECTIONS_PER_NODE = config("ELASTIC_CONNECTIONS_PER_NODE", cast=int, default=10)
    ELASTIC_TIMEOUT = config("ELASTIC_TIMEOUT", cast=int, default=30)
    ELASTIC_MAX_RETRIES = config("ELASTIC_MAX_RETRIES", cast=int, default=3)


class LogConfig(BaseConfig):
    APPLICATION_LOG_LEVEL = config("APPLICATION_LOG_LEVEL", default="INFO")
    ELK_TRANSPORT_LOG_LEVEL = config("ELK_TRANSPORT_LOG_LEVEL", default="WARNING")


class GunicornConfig(BaseConfig):
    GUNICORN_HOST = config("GUNICORN_HOST", default="0.0.0.0")
    GUNICORN_PORT = config("GUNICORN_PORT", cast=int)
    GUNICORN_LOG_LEVEL = config("GUNICORN_LOG_LEVEL", cast=str ,default="INFO")
    GUNICORN_TIMEOUT = config("GUNICORN_TIMEOUT", cast=int, default=300)


class SentryConfig(BaseConfig):
    if BaseConfig.is_production():
        SENTRY_DSN = config("SENTRY_DSN")
        TRACES_SAMPLE_RATE = config("TRACES_SAMPLE_RATE", cast=float)