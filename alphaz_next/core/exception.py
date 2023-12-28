class InvalidCredentialsError(Exception):
    def __init__(self):
        super().__init__("Could not validate credentials")


class NotEnoughPermissionsError(Exception):
    def __init__(self):
        super().__init__("Not enough permissions")
