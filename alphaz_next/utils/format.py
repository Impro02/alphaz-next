# MODULES
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# PYDANTIC
from pydantic import BaseModel

# SQLALCHEMY
from sqlalchemy.orm import InstrumentedAttribute, RelationshipProperty


def uppercase(items: list[str] | str):
    if items is None:
        return

    if isinstance(items, list):
        return [item.strip().upper() for item in items]
    if isinstance(items, set):
        return {item.strip().upper() for item in items}
    else:
        return items.strip().upper()


def create_model_column_enum(model, exclude: list[str] = []):
    return create_enum(
        enum_name=f"{model.__name__}Enum",
        values=sorted(
            [
                attr.key
                for attr in model.__dict__.values()
                if isinstance(attr, InstrumentedAttribute)
                and not isinstance(attr.property, RelationshipProperty)
                and attr.key not in exclude
            ]
        ),
    )


def create_enum(enum_name, values) -> Enum:
    enum_members = {}
    for value in values:
        enum_members[value] = value
    return Enum(enum_name, enum_members)


def is_field_in_model(
    model,
    field: str,
    mapper_alias: Dict[str, Optional[str]],
) -> bool:
    field_alias = mapper_alias.get(field)
    item = field_alias if field_alias is not None else field
    base_model_fields = [
        attr.key
        for attr in model.__dict__.values()
        if isinstance(attr, InstrumentedAttribute)
        and not isinstance(attr.property, RelationshipProperty)
    ]
    return item in base_model_fields


def get_mapper_enum(model, schema: BaseModel) -> Tuple[Dict[str, Optional[str]], Enum]:
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
    return date_str.replace("T", " ")


def extract_value_from_enum(data: Union[Enum, List[Enum]]):
    if isinstance(data, list):
        return [item.value for item in data]

    return data.value


def extract_order_with_alias(items: Union[List[Enum], Enum], mapper: Dict[str, Any]):
    return [mapper.get(item) or item for item in extract_value_from_enum(items)]


def nonesorter(a):
    if not a:
        return ""
    return a
