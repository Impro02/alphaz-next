# PYDANTIC
from pydantic import Field
from pydantic_settings import BaseSettings


class AlphaInternalConfigSettingsSchema:
    token_url: str
    user_me_url: str
    api_key_me_url: str
    secret_key: str
    algorithm: str


def create_internal_config(
    token_url_alias: str = "ALPHA_TOKEN_URL",
    user_me_url_alias: str = "ALPHA_USER_ME_URL",
    api_key_me_url_alias: str = "ALPHA_API_KEY_ME_URL",
    secret_key_alias: str = "ALPHA_SECRET_KEY",
    algorithm_alias: str = "ALPHA_ALGORITHM",
) -> AlphaInternalConfigSettingsSchema:
    """
    Create an instance of the AlphaInternalConfigSettingsSchema class with the provided configuration settings.

    Args:
        token_url_alias (str, optional): The alias for the token URL. Defaults to "ALPHA_TOKEN_URL".
        user_me_url_alias (str, optional): The alias for the user me URL. Defaults to "ALPHA_USER_ME_URL".
        api_key_me_url_alias (str, optional): The alias for the API key me URL. Defaults to "ALPHA_API_KEY_ME_URL".
        secret_key_alias (str, optional): The alias for the secret key. Defaults to "ALPHA_SECRET_KEY".
        algorithm_alias (str, optional): The alias for the algorithm. Defaults to "ALPHA_ALGORITHM".

    Returns:
        AlphaInternalConfigSettingsSchema: An instance of the AlphaInternalConfigSettingsSchema class.
    """

    class _AlphaInternalConfigSettingsSchema(
        BaseSettings,
        AlphaInternalConfigSettingsSchema,
    ):
        token_url: str = Field(
            default="/auth",
            validation_alias=token_url_alias,
        )
        user_me_url: str = Field(
            default="user/me",
            validation_alias=user_me_url_alias,
        )
        api_key_me_url: str = Field(
            default="api-key/me",
            validation_alias=api_key_me_url_alias,
        )
        secret_key: str = Field(
            default="",
            validation_alias=secret_key_alias,
        )
        algorithm: str = Field(
            default="",
            validation_alias=algorithm_alias,
        )

    return _AlphaInternalConfigSettingsSchema()
