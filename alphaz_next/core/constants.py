from enum import Enum


class HeaderEnum(Enum):
    STATUS_DESCRIPTION = "x-status-description"
    PAGINATION = "x-pagination"
    PROCESS_TIME = "x-process-time"
    WARNING = "x-warning"
