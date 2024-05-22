# MODULES
from typing import (
    List as _List,
    Optional as _Optional,
    Type as _Type,
)

# PYSQL_REPO
from pysql_repo import DataBase as _DataBase
from pysql_repo._database_base import (
    DataBaseConfigTypedDict as _DataBaseConfigTypedDict,
)

# SQLALCHEMY
from sqlalchemy import MetaData as _MetaData
from sqlalchemy.orm import DeclarativeBase as _DeclarativeBase

# OPENTELEMETRY
from opentelemetry.instrumentation.sqlalchemy import (
    SQLAlchemyInstrumentor as _SQLAlchemyInstrumentor,
)


class DataBase(_DataBase):

    def __init__(
        self,
        databases_config: _DataBaseConfigTypedDict,
        base: _Type[_DeclarativeBase],
        metadata_views: _Optional[_List[_MetaData]] = None,
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

        _SQLAlchemyInstrumentor().instrument(engine=self._engine)
