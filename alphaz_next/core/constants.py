from enum import Enum


class HeaderEnum(Enum):
    """
    Enum class representing header constants.
    """

    STATUS_DESCRIPTION = "x-status-description"
    PAGINATION = "x-pagination"
    PROCESS_TIME = "x-process-time"
    WARNING = "x-warning"
