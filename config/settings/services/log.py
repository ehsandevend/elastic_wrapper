import orjson
import logging

from config.settings.integrations_config import LogConfig
from shared.enums import LogChoices


class CustomJsonFormatter(logging.Formatter):

    def format(self, record):
        log_record = {}

        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["loglevel"] = record.levelname
        log_record["message"] = record.getMessage()
        log_record["logger"] = record.name

        if hasattr(record, "data"):
            log_record["data"] = record.data

        log_record["environmentName"] = LogConfig.ENVIRONMENT

        return orjson.dumps(
            log_record,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_APPEND_NEWLINE
        ).decode("utf-8")


def get_logging_config():
    """
    Get the logging configuration dictionary.
    This centralizes all logging configuration in one place.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "config.settings.services.log.CustomJsonFormatter",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": LogConfig.APPLICATION_LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": LogConfig.APPLICATION_LOG_LEVEL,
            "handlers": ["console"],
        },
        "loggers": {
            "elastic_transport.transport": {
                "level": LogConfig.ELK_TRANSPORT_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            LogChoices.INGESTOR: {
                "level": LogConfig.APPLICATION_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }


def setup_logging():
    config_dict = get_logging_config()
    logging.config.dictConfig(config_dict)
    return logging.getLogger(LogChoices.INGESTOR)
