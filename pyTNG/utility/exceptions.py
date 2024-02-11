"""
Exceptions specific to the pyTNG package.
"""


class APIKeyError(Exception):
    """
    Error raised when an API key is not locatable.
    """

    def __init__(self):
        self.message = "Backend failed to find API key. This can be set in the /bin/config.yaml file."
        super.__init__()
