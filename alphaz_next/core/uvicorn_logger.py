# MODULES
import logging
from typing import List


class ExcludeRoutersFilter(logging.Filter):
    def __init__(self, router_names: List[str]):
        super().__init__()
        self.router_names = router_names

    def filter(self, record):
        for router_name in self.router_names:
            if record.getMessage().startswith(f'"{router_name.upper()} '):
                return False
        return True


_uvicorn_access = logging.getLogger("uvicorn.access")
_uvicorn_access.disabled = True

UVICORN_LOGGER = logging.getLogger("uvicorn")
UVICORN_LOGGER.addFilter(ExcludeRoutersFilter(["status"]))
