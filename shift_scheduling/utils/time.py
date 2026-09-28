""""""

from datetime import UTC, datetime


def parse_time(value: str) -> datetime:
    """
    Parse an ISO-8601 timestamp into an aware UTC datetime.

    Args:
        value: The ISO-8601 timestamp to parse.

    Returns:
        The parsed datetime.
    """
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def format_time(value: datetime) -> str:
    """
    Format an aware UTC datetime as an ISO-8601 timestamp.

    Args:
        value: The datetime to format.

    Returns:
        The formatted timestamp.
    """
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
