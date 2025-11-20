class InvalidLoggerNameError(Exception):
    def __init__(self, name: str, allowed_loggers: list):
        message = (
            f"Logger name '{name}' is not allowed. "
            f"Only loggers from LogChoices are permitted: {allowed_loggers}. "
            f"To add a new logger, Add it to LogChoices enum."
        )
        super().__init__(message)
