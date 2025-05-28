# skills/fallback.py


def get_fallback_response(query: str) -> str:
    return (
        "This answer may not be reliable. Please consult a "
        + " professional healthcare provider for guidance on: {query}"
    )
