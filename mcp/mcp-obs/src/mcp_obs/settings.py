"""Settings for the observability MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    victorialogs_url: str
    victoriatraces_url: str


def resolve_settings() -> Settings:
    victorialogs_url = os.environ.get(
        "NANOBOT_VICTORIALOGS_URL",
        "http://localhost:42010",
    )
    victoriatraces_url = os.environ.get(
        "NANOBOT_VICTORIATRACES_URL",
        "http://localhost:42011",
    )
    return Settings(
        victorialogs_url=victorialogs_url,
        victoriatraces_url=victoriatraces_url,
    )
