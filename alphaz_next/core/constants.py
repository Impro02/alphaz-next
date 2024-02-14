from enum import Enum


class HeaderEnum(Enum):
    """
    Enum class representing header constants.
    """

    ACCESS_CONTROL_ALLOW_PRIVATE_NETWORK = "Access-Control-Allow-Private-Network"
    STATUS_DESCRIPTION = "x-status-description"
    PAGINATION = "x-pagination"
    PROCESS_TIME = "x-process-time"
    WARNING = "x-warning"
