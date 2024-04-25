# PYSQL_REPO
from pysql_repo import DataBase as _DataBase

# OPENTELEMETRY
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


class DataBase(_DataBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        SQLAlchemyInstrumentor().instrument(engine=self._engine)
