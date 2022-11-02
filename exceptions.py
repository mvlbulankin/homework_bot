class EnvironmentsMissingException(Exception):
    """One or more environments are missing"""

    pass


class NotForSend(Exception):
    """Exception not for forwarding to telegram."""

    pass
