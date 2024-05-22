# MODULES
from typing import (
    List as _List,
    Optional as _Optional,
    Type as _Type,
)

# PYSQL_REPO
from pysql_repo.asyncio import AsyncDataBase as _AsyncDataBase
from pysql_repo._database_base import (
    DataBaseConfigTypedDict as _DataBaseConfigTypedDict,
)

# SQLALCHEMY
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# OPENTELEMETRY
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


class AsyncDataBase(_AsyncDataBase):

    def __init__(
        self,
        databases_config: _DataBaseConfigTypedDict,
        base: _Type[DeclarativeBase],
        metadata_views: _Optional[_List[MetaData]] = None,
        autoflush: bool = False,
        expire_on_commit: bool = False,
        echo: bool = False,
    ) -> None:
        super().__init__(
            databases_config=databases_config,
            base=base,
            metadata_views=metadata_views,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            echo=echo,
        )

        SQLAlchemyInstrumentor().instrument(engine=self._engine.sync_engine)
