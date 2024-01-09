# MODULES
import os
import pytz
import re
from typing import Dict, Generator, List, Optional, TypedDict
from pathlib import Path
from datetime import datetime
from logging import Logger

# SQLALCHEMY
from sqlalchemy import create_engine, orm, Table, text
from sqlalchemy.orm import Session, DeclarativeMeta
from sqlalchemy.schema import sort_tables
from sqlalchemy.inspection import inspect

# CONTEXTLIB
from contextlib import contextmanager

# LIBS
from alphaz_next.libs.file_lib import open_json_file


class DataBaseConfigTypedDict(TypedDict):
    connection_string: str
    ini: bool
    init_database_dir_json: Optional[str]
    pool_size: int
    connect_args: Optional[Dict]


class AlphaDatabase:
    def __init__(
        self,
        databases_config: DataBaseConfigTypedDict,
        base: DeclarativeMeta,
        logger: Logger,
    ) -> None:
        self._database_config = databases_config
        self._engine = create_engine(
            self._database_config.get("connection_string"),
            echo=False,
            connect_args=self._database_config.get("connect_args") or {},
        )
        self._base = base
        self._logger = logger

        self._session_factory = orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )

    @property
    def ini(self):
        return self._database_config.get("ini")

    @property
    def init_database_dir_json(self):
        return self._database_config.get("init_database_dir_json")

    def create_database(
        self, view_names: List[Table] = None
    ) -> None:  # TODO find a way to get view names automatically
        insp = inspect(self._engine)
        current_view_names = [item.lower() for item in insp.get_view_names()]

        with self.session_factory() as session:
            for view in view_names or []:
                if view.name.lower() in current_view_names:
                    session.execute(text(f"DROP VIEW {view}"))

        self._base.metadata.create_all(self._engine)

    @contextmanager
    def session_factory(self) -> Generator[Session, None, None]:
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
        if not (init := self.ini):
            raise ValueError(
                f"Unable to init database tables because {init=} in config"
            )

        def _post_process(data: dict):
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

        if directory is None:
            directory = self._database_config.init_database_dir_json

        table_names = table_names or set()
        tables = {
            k: v for k, v in self._base.metadata.tables.items() if k in table_names
        }

        ordered_tables: list[Table] = sort_tables(tables.values())

        with self.session_factory() as session:
            for table in ordered_tables:
                table_name = str(table.name).upper()
                path = directory / f"{table_name}.json"

                session.execute(table.delete())

                if not os.path.exists(path):
                    self._logger.warning(
                        f"Failed to initialize {table_name=} due to the absence of the file at [{path}]."
                    )
                else:
                    raw_data = open_json_file(path=path)

                    raw_data = [_post_process(data) for data in raw_data]

                    session.execute(table.insert().values(raw_data))

                    self._logger.info(
                        f"Successfully initialized {table_name=} from the file at {path}."
                    )

                session.commit()

        return ordered_tables
