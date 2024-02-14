"""
Exceptions specific to the pyTNG package.
"""


class APIKeyError(Exception):
    """
    Error raised when an API key is not locatable.
    """

    def __init__(self):
        self.message = "Backend failed to find API key. Use pytng-apikey <API-KEY> to set the API key."
        super().__init__(self.message)
