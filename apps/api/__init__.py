"""
FastAPI application package for ReliQuary.

Importing this package is intentionally lightweight. The FastAPI app is loaded
from apps.api.main only when explicitly requested, so service imports do not
pull in auth/JWT dependencies as a side effect.
"""


def __getattr__(name: str):
    if name in {
        "app",
        "get_app",
        "configure_middleware",
        "configure_routes",
        "configure_exception_handlers",
    }:
        from . import main

        return getattr(main, name)
    raise AttributeError(name)


__all__ = [
    "app",
    "get_app",
    "configure_middleware",
    "configure_routes",
    "configure_exception_handlers",
]
