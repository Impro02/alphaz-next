# MODULES
import logging


_uvicorn_access = logging.getLogger("uvicorn.access")
_uvicorn_access.disabled = True

UVICORN_LOGGER = logging.getLogger("uvicorn")
