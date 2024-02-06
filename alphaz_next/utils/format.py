# MODULES
from enum import Enum as _Enum
from typing import (
    Any as _Any,
    Dict as _Dict,
    List as _List,
    Optional as _Optional,
    Tuple as _Tuple,
    Type as _Type,
    TypeVar as _TypeVar,
    Union as _Union,
)

# PYDANTIC
from pydantic import BaseModel as _BaseModel

# SQLALCHEMY
from sqlalchemy.orm import (
    InstrumentedAttribute as _InstrumentedAttribute,
    RelationshipProperty as _RelationshipProperty,
    declarative_base as _declarative_base,
)

_T = _TypeVar("_T", bound=_declarative_base())


def uppercase(items: _List[str] | str) -> _List[str] | str:
    """
    Converts the given string or list of strings to uppercase.

    Args:
        items (list[str] | str): The string or list of strings to be converted.

    Returns:
        str | list[str]: The converted string or list of strings in uppercase.

    Example:
        >>> uppercase("hello")
        'HELLO'

        >>> uppercase(["hello", "world"])
        ['HELLO', 'WORLD']
    """
    if items is None:
        return

    if isinstance(items, list):
        return [item.strip().upper() for item in items]
    if isinstance(items, set):
        return {item.strip().upper() for item in items}
    else:
        return items.strip().upper()


def create_model_column_enum(model: _Type[_T], exclude: list[str] = []) -> _Enum:
    """
    Create an enum for the columns of a SQLAlchemy model.

    Args:
        model (Type[_T]): The SQLAlchemy model for which to create the enum.
        exclude (List[str]): A list of column names to exclude from the enum.

    Returns:
        An enum representing the columns of the model.
    """
    return create_enum(
        enum_name=f"{model.__name__}Enum",
        values=sorted(
            [
                attr.key
                for attr in model.__dict__.values()
                if isinstance(attr, _InstrumentedAttribute)
                and not isinstance(attr.property, _RelationshipProperty)
                and attr.key not in exclude
            ]
        ),
    )


def create_enum(enum_name: str, values: _List[_Any]) -> _Enum:
    """
    Create an enumeration with the given name and values.

    Args:
        enum_name (str): The name of the enumeration.
        values (List[Any]): A list of values for the enumeration.

    Returns:
        Enum: The created enumeration.
    """
    enum_members = {}
    for value in values:
        enum_members[value] = value
    return _Enum(enum_name, enum_members)


def is_field_in_model(
    model: _Type[_T],
    field: str,
    mapper_alias: _Dict[str, _Optional[str]],
) -> bool:
    """
    Check if a field is present in a model.

    Args:
        model: The model to check.
        field: The field to check.
        mapper_alias: A dictionary mapping field names to their aliases.

    Returns:
        bool: True if the field is present in the model, False otherwise.
    """
    field_alias = mapper_alias.get(field)
    item = field_alias if field_alias is not None else field
    base_model_fields = [
        attr.key
        for attr in model.__dict__.values()
        if isinstance(attr, _InstrumentedAttribute)
        and not isinstance(attr.property, _RelationshipProperty)
    ]
    return item in base_model_fields


def get_mapper_enum(
    model: _Type[_T],
    schema: _BaseModel,
) -> _Tuple[_Dict[str, _Optional[str]], _Enum]:
    """
    Get the mapper alias dictionary and enum for the given model and schema.

    Args:
        model: The model object.
        schema: The schema object.

    Returns:
        A tuple containing the mapper alias dictionary and the enum.
    """
    mapper_alias = {k: v.alias for k, v in schema.model_fields.items()}
    enum = create_enum(
        "CONFIG_CATEGORY_ENUM",
        [
            item
            for item in schema.model_fields.keys()
            if is_field_in_model(model, item, mapper_alias)
        ],
    )

    return mapper_alias, enum


def remove_t_from_date_str(date_str: str) -> str:
    """
    Removes the 'T' character from a date string and replaces it with a space.

    Args:
        date_str (str): The date string to be formatted.

    Returns:
        str: The formatted date string with 'T' replaced by a space.
    """
    return date_str.replace("T", " ")


def extract_value_from_enum(
    data: _Union[_Enum, _List[_Enum]]
) -> _Union[_Any, _List[_Any]]:
    """
    Extracts the value(s) from an Enum or a list of Enums.

    Args:
        data (Union[Enum, List[Enum]]): The Enum or list of Enums from which to extract the values.

    Returns:
        Union[Any, List[Any]]: The extracted value(s) from the Enum(s).
    """
    if isinstance(data, list):
        return [item.value for item in data]

    return data.value


def extract_order_with_alias(
    items: _Union[_List[_Enum], _Enum],
    mapper: _Dict[str, _Any],
) -> _List[_Any]:
    """
    Extracts the order with alias from the given items using the provided mapper.

    Args:
        items (Union[List[Enum], Enum]): The items to extract the order with alias from.
        mapper (Dict[str, Any]): The mapper containing the alias mappings.

    Returns:
        List[Any]: The list of items with the order replaced by the alias if available in the mapper.
    """
    return [mapper.get(item) or item for item in extract_value_from_enum(items)]


def nonesorter(a: _Any) -> _Any:
    """
    Sorts a value, treating None as an empty string.

    Args:
        a (Any): The value to be sorted.

    Returns:
        Any: The sorted value, with None treated as an empty string.
    """
    if not a:
        return ""
    return a
