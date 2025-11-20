from config.settings.integrations_config import BaseConfig


def add_trusted_host_middleware(app):
    from starlette.middleware.trustedhost import TrustedHostMiddleware

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=BaseConfig.ALLOWED_HOSTS,
    )


def add_cors_middleware(app):
    from fastapi.middleware.cors import CORSMiddleware

    #TODO: add ALLOW_ORIGINS to env
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
