class EnvironmentsMissingException(Exception):
    """One or more environments are missing"""

    pass


class NotForSendException(Exception):
    """Exception not for forwarding to telegram."""

    pass
