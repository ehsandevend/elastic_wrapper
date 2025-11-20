from config.settings.integrations_config import BaseConfig


def setup_prometheus(app):
    if BaseConfig.is_production():
        from prometheus_fastapi_instrumentator import Instrumentator

        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/docs", "/redoc", "/openapi.json", "/favicon.ico"],
            inprogress_labels=True,
        )
        instrumentator.instrument(app).expose(app)