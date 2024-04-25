# PYSQL_REPO
from pysql_repo.asyncio import AsyncDataBase as _AsyncDataBase

# OPENTELEMETRY
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


class AsyncDataBase(_AsyncDataBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        SQLAlchemyInstrumentor().instrument(engine=self._engine.sync_engine)
