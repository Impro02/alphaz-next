# PYDANTIC
from pydantic import Field
from pydantic_settings import BaseSettings


def create_internal_config(
    auth_url_alias: str = "AUTH_URL",
    user_me_url_alias: str = "USER_ME_URL",
    api_key_me_url_alias: str = "API_KEY_ME_URL",
    secret_key_alias: str = "SECRET_KEY",
    algorithm_alias: str = "ALGORITHM",
):
    class AlphaInternalConfigSettingsSchema(BaseSettings):
        auth_url: str = Field(validation_alias=auth_url_alias)
        user_me_url: str = Field(validation_alias=user_me_url_alias)
        api_key_me_url: str = Field(validation_alias=api_key_me_url_alias)
        secret_key: str = Field(validation_alias=secret_key_alias)
        algorithm: str = Field(validation_alias=algorithm_alias)

    return AlphaInternalConfigSettingsSchema()
