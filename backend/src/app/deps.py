from typing import Any


def make_response(data: Any, *, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "data": data,
        "meta": meta or {},
        "error": None,
    }
