# MODULES
import os
import pytz
import re
from typing import Any, Dict, Generator, List, Optional, TypedDict
from pathlib import Path
from datetime import datetime
from logging import Logger

# SQLALCHEMY
from sqlalchemy import Table, text, MetaData, Connection, orm, create_engine
from sqlalchemy.orm import DeclarativeMeta, Session
from sqlalchemy.schema import sort_tables
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

# CONTEXTLIB
from contextlib import asynccontextmanager, contextmanager

# LIBS
from alphaz_next.libs.file_lib import open_json_file


class _DataBaseConfigTypedDict(TypedDict):
    connection_string: str
    ini: bool
    init_database_dir_json: Optional[str]
    create_on_start: bool
    connect_args: Optional[Dict]


class _Database:
    def __init__(
        self,
        databases_config: _DataBaseConfigTypedDict,
        logger: Logger,
        base: DeclarativeMeta,
        metadata_views: Optional[List[MetaData]] = None,
    ) -> None:
        self._database_config = databases_config
        self._logger = logger
        self._base = base
        self._metadata_views = metadata_views

        self._views = [
            table
            for metadata in self._metadata_views or []
            for table in metadata.sorted_tables
        ]

    @property
    def views(self) -> List[Table]:
        return self._views

    @property
    def ini(self):
        return self._database_config.get("ini")

    @property
    def init_database_dir_json(self):
        return self._database_config.get("init_database_dir_json")

    @classmethod
    def _pre_process_data_for_initialization(cls, data: Dict[str, Any], timezone: str):
        for key, value in data.items():
            if isinstance(value, str) and re.match(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?(Z|[+-]\d{2}:?\d{2})?",
                value,
            ):
                if value.endswith("Z"):
                    utc_dt = datetime.fromisoformat(value[:-1])
                    local_tz = pytz.timezone(timezone)
                    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
                    data[key] = local_dt
                else:
                    data[key] = datetime.fromisoformat(value)

        return data

    def _get_pre_process_data_for_initialization(
        self,
        path: Path,
        timezone: str,
    ) -> Optional[List[Dict[str, Any]]]:
        try:
            raw_data = open_json_file(path=path)
        except FileNotFoundError:
            self._logger.warning(
                f"Failed to initialize table due to the absence of the file at [{path}]."
            )

            return

        return [
            self._pre_process_data_for_initialization(
                data,
                timezone=timezone,
            )
            for data in raw_data
        ]

    def _get_ordered_tables(self, table_names: List[str]) -> List[Table]:
        if not (init := self.ini):
            raise ValueError(
                f"Unable to init database tables because {init=} in config"
            )

        if directory is None:
            directory = self.init_database_dir_json

        table_names = table_names or set()
        tables = {
            k: v for k, v in self._base.metadata.tables.items() if k in table_names
        }

        return sort_tables(tables.values())


class AlphaDataBase(_Database):
    def __init__(
        self,
        databases_config: _DataBaseConfigTypedDict,
        logger: Logger,
        base: DeclarativeMeta,
        metadata_views: List[MetaData] | None = None,
    ) -> None:
        super().__init__(databases_config, logger, base, metadata_views)

        self._engine = create_engine(
            self._database_config.get("connection_string"),
            echo=False,
            connect_args=self._database_config.get("connect_args") or {},
        )

        self._session_factory = orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )

        if self._database_config.get("create_on_start"):
            self.create_database()

    def create_database(self) -> None:
        insp = inspect(self._engine)
        current_view_names = [item.lower() for item in insp.get_view_names()]

        with self.session_factory() as session:
            for view in self.views:
                if view.key.lower() in current_view_names:
                    session.execute(text(f"DROP VIEW {view}"))

        self._base.metadata.create_all(self._engine)

    @contextmanager
    def session_factory(self) -> Generator[Session, Any, None]:
        session = self._session_factory()
        try:
            yield session
        except Exception as ex:
            self._logger.error("Session rollback because of exception", exc_info=ex)
            session.rollback()
            raise
        finally:
            session.close()

    def init_tables_from_json_files(
        self,
        directory: Path,
        table_names: list[str],
        timezone="CET",
    ):
        ordered_tables = self._get_ordered_tables(table_names=table_names)

        with self.session_factory() as session:
            for table in ordered_tables:
                path = directory / f"{(table_name := table.name.upper())}.json"

                raw_data = self._get_pre_process_data_for_initialization(
                    path=path,
                    timezone=timezone,
                )

                if raw_data is None:
                    continue

                session.execute(table.insert().values(raw_data))

                self._logger.info(
                    f"Successfully initialized {table_name=} from the file at {str(path)}."
                )

                session.commit()

        return ordered_tables


class AsyncAlphaDatabase(_Database):
    def __init__(
        self,
        databases_config: _DataBaseConfigTypedDict,
        logger: Logger,
        base: DeclarativeMeta,
        metadata_views: Optional[List[MetaData]] = None,
    ) -> None:
        self._database_config = databases_config
        self._engine = create_async_engine(
            self._database_config.get("connection_string"),
            echo=False,
            connect_args=self._database_config.get("connect_args") or {},
        )
        self._logger = logger
        self._base = base
        self._metadata_views = metadata_views

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
        )

        self._views = [
            table
            for metadata in self._metadata_views or []
            for table in metadata.sorted_tables
        ]

        if self._database_config.get("create_on_start"):
            self.create_database()

    async def create_database(self) -> None:
        def inspect_view_names(conn: Connection):
            inspector = inspect(conn)

            return [item.lower() for item in inspector.get_view_names()]

        async with self._engine.connect() as conn:
            current_view_names = await conn.run_sync(inspect_view_names)

        async with self.session_factory() as session:
            for view in self.views:
                if view.key.lower() in current_view_names:
                    await session.execute(text(f"DROP VIEW {view}"))

        self._base.metadata.create_all(self._engine)

    @asynccontextmanager
    async def session_factory(self) -> Generator[AsyncSession, Any, None]:
        async with self._session_factory() as session:
            try:
                yield session
            except Exception as ex:
                self._logger.error("Session rollback because of exception", exc_info=ex)
                await session.rollback()
                raise ex
            finally:
                await session.close()

    async def init_tables_from_json_files(
        self,
        directory: Path,
        table_names: List[str],
        timezone: str = "CET",
    ):
        ordered_tables = self._get_ordered_tables(table_names=table_names)

        async with self.session_factory() as session:
            for table in ordered_tables:
                path = directory / f"{(table_name := table.name.upper())}.json"

                raw_data = self._get_pre_process_data_for_initialization(
                    path=path,
                    timezone=timezone,
                )

                if raw_data is None:
                    continue

                await session.execute(table.delete())
                await session.execute(table.insert().values(raw_data))

                self._logger.info(
                    f"Successfully initialized {table_name=} from the file at {str(path)}."
                )

            await session.commit()

        return ordered_tables
