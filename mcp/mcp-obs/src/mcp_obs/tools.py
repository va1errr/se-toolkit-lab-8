"""Tool schemas, handlers, and registry for the observability MCP server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_obs.client import ObservabilityClient


ToolPayload = BaseModel | list[dict] | dict
ToolHandler = Callable[[ObservabilityClient, BaseModel], Awaitable[ToolPayload]]


class LogsSearchParams(BaseModel):
    query: str = Field(description="LogsQL query string, e.g., '_time:10m severity:ERROR'")
    limit: int = Field(default=100, ge=1, le=1000, description="Max results to return")


class LogsErrorCountParams(BaseModel):
    service: str | None = Field(default=None, description="Filter by service name")
    time_range: str = Field(default="1h", description="Time range like '1h', '10m', '24h'")


class TracesListParams(BaseModel):
    service: str | None = Field(default=None, description="Filter by service name")
    limit: int = Field(default=20, ge=1, le=100, description="Max traces to return")


class TracesGetParams(BaseModel):
    trace_id: str = Field(description="Trace ID to fetch")


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _logs_search(client: ObservabilityClient, args: LogsSearchParams) -> ToolPayload:
    results = await client.logs_query(args.query, args.limit)
    return results


async def _logs_error_count(client: ObservabilityClient, args: LogsErrorCountParams) -> ToolPayload:
    result = await client.logs_error_count(args.service, args.time_range)
    return result


async def _traces_list(client: ObservabilityClient, args: TracesListParams) -> ToolPayload:
    results = await client.traces_list(args.service, args.limit)
    return results


async def _traces_get(client: ObservabilityClient, args: TracesGetParams) -> ToolPayload:
    result = await client.traces_get(args.trace_id)
    return result


TOOL_SPECS = (
    ToolSpec(
        "logs_search",
        "Search logs using LogsQL query. Use fields like service.name, severity, event, trace_id.",
        LogsSearchParams,
        _logs_search,
    ),
    ToolSpec(
        "logs_error_count",
        "Count errors by service over a time window. Returns total and breakdown by service.",
        LogsErrorCountParams,
        _logs_error_count,
    ),
    ToolSpec(
        "traces_list",
        "List recent traces. Optionally filter by service name.",
        TracesListParams,
        _traces_list,
    ),
    ToolSpec(
        "traces_get",
        "Fetch a specific trace by ID. Returns full span hierarchy.",
        TracesGetParams,
        _traces_get,
    ),
)
TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
