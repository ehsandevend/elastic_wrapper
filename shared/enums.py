from enum import StrEnum


class LogChoices(StrEnum):
    INGESTOR = "INGESTOR"


class ModelTagChoices(StrEnum):
    E_DAMAGE_REQUEST = "DamageRequest"
    DOCUMENT = "HealthClaimDocument"
    CLAIM = "HealthInsuredClaim"
    CLAIM_JUNCTION = "HealthInsuredClaimEclaim"


class EnvironmentChoices(StrEnum):
    DEV = "development"
    PROD = "production"


class ElkClientTypeChoices(StrEnum):
    READ = "read"
    WRITE = "write"