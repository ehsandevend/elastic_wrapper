from config.settings.integrations_config import SentryConfig


def setup_sentry():
    if SentryConfig.is_production():
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_sdk.init(
            dsn=SentryConfig.SENTRY_DSN,
            integrations=[
                FastApiIntegration(),
                LoggingIntegration(level=None, event_level=None),
            ],
            traces_sample_rate=SentryConfig.TRACES_SAMPLE_RATE,
            send_default_pii=True,
            environment=SentryConfig.ENVIRONMENT,
        )
