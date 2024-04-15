## Alphaz-Next
Alphaz-Next is a Python library designed to simplify the setup of REST APIs using FastAPI & Pydantic. It provides a useful toolkit for setting up Logger, Config, and more.

## Installing

To install alphaz-next, if you already have Python, you can install with:

```bash
pip install alphaz-next
```

## Usage

To use Alphaz-Next in your Python code, import the necessary classes and functions like this:

```
from alphaz-next import DataBase, Logger
from alphaz-next.models.config.config_settings import create_config_settings
```

## Features

### Logger Setup

The `Logger` class provides a custom logging functionality with various log levels and output options. It is imported from the `alphaz_next.utils.logger` module.

#### Initialization

The `Logger` class is initialized with the following parameters:

- `name` (str): The name of the logger.
- `directory` (str): The directory where the log files will be stored.
- `level` (int, optional): The log level. Defaults to `logging.INFO`.
- `stream_output` (bool, optional): If set to `True`, the logs will also be output to the console. Defaults to `True`.
- `when` (str, optional): Specifies when to rotate the log file. Defaults to `"midnight"`.
- `interval` (int, optional): The interval at which the log file should be rotated. Defaults to `1`.
- `backup_count` (int, optional): The number of backup log files to keep. Defaults to `10`.
- `file_name` (str, optional): The name of the log file. If not provided, the log file will be named after the logger. Defaults to `None`.
- `logging_formatter` (str, optional): The format string for the log messages. Defaults to `DEFAULT_FORMAT`.
- `date_formatter` (str, optional): The format string for the date in the log messages. Defaults to `DEFAULT_DATE_FORMAT`.

#### Usage

Here's an example of how to use the `Logger` class:

```python
from alphaz_next.utils.logger import Logger

logger = Logger(
    name="my_logger",
    directory="/path/to/log/files",
    level=logging.INFO,
    stream_output=True,
    when="midnight",
    interval=1,
    backup_count=10,
    file_name=None,
    logging_formatter=DEFAULT_FORMAT,
    date_formatter=DEFAULT_DATE_FORMAT
)

logger.info("This is an info log message.")
```

## Database Connection Setup
The Database class represents a database connection and provides methods for various database operations.

### Initialization
The Database class is initialized with the following parameters:

- databases_config (_DataBaseConfigTypedDict): A dictionary containing the configuration for the databases.
- logger (Logger): The logger object to be used for logging.
- base (DeclarativeMeta): The base class for the declarative models.
- metadata_views (List[MetaData] | None, optional): A list of metadata views. Defaults to None.

### Usage

Here's an example of how to use the `DataBase` class:

```python
from alphaz_next import DataBase, Logger

# Initialize the logger
logger = Logger(
    name='sqlalchemy.engine', 
    file_name="database", 
    stream_output=False, 
    level=logging.DEBUG
)

# Create the database configuration
databases_config = {
    "mydb1": {
        "host": "srv-mydb1-db-dev.example.com",
        "password": "MyDB1Dev_123",
        "username": "mydb1adm",
        "port": 1234,
        "driver": "oracledb",
        "service_name": "mydb1",
        "ini": false
    },
    "mydb2": {
        "path": "{{project}}/mydb2.sqlite",
        "driver": "sqlite",
        "ini": true,
        "init_database_dir_json": "{{project}}/tests/mydb2/ini",
        "connect_args": {
            "check_same_thread": false
        }
    }
}

# Initialize the database connection
database = DataBase(
    databases_config=databases_config, 
    logger=logger, 
    base=Base
)

# Use the database connection
with database.session_factory() as session:
    # Perform database operations...

```