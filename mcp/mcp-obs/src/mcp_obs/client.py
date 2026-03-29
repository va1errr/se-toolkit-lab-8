"""Async HTTP client for VictoriaLogs and VictoriaTraces APIs."""

from __future__ import annotations

import json

import httpx


class ObservabilityClient:
    """Client for VictoriaLogs and VictoriaTraces APIs."""

    def __init__(
        self,
        victorialogs_url: str,
        victoriatraces_url: str,
        *,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.victorialogs_url = victorialogs_url.rstrip("/")
        self.victoriatraces_url = victoriatraces_url.rstrip("/")
        self._owns_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> ObservabilityClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client and self._http_client:
            await self._http_client.aclose()

    async def logs_query(self, query: str, limit: int = 100) -> list[dict]:
        """Query VictoriaLogs using LogsQL."""
        url = f"{self.victorialogs_url}/select/logsql/query"
        response = await self._http_client.get(
            url,
            params={"query": query, "limit": limit},
        )
        response.raise_for_status()
        # VictoriaLogs returns a stream of JSON lines or array
        content = response.text.strip()
        if content.startswith("["):
            return response.json()
        # Parse JSON lines
        results = []
        for line in content.split("\n"):
            if line.strip():
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    results.append({"raw": line})
        return results

    async def logs_error_count(
        self, service: str | None = None, time_range: str = "1h"
    ) -> dict:
        """Count errors by service over a time window."""
        query = f"_time:{time_range} severity:ERROR"
        if service:
            query += f' service.name:"{service}"'
        results = await self.logs_query(query, limit=1000)
        # Count by service
        by_service: dict[str, int] = {}
        for entry in results:
            svc = entry.get("service.name", "unknown")
            by_service[svc] = by_service.get(svc, 0) + 1
        return {"time_range": time_range, "by_service": by_service, "total": sum(by_service.values())}

    async def traces_list(self, service: str | None = None, limit: int = 20) -> list[dict]:
        """List recent traces from VictoriaTraces."""
        url = f"{self.victoriatraces_url}/select/jaeger/api/traces"
        params = {"limit": limit}
        if service:
            params["service"] = service
        response = await self._http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # Jaeger API returns {"data": [...]}
        return data.get("data", [])

    async def traces_get(self, trace_id: str) -> dict:
        """Get a specific trace by ID."""
        url = f"{self.victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
        response = await self._http_client.get(url)
        response.raise_for_status()
        data = response.json()
        # Jaeger API returns {"data": [...]}
        traces = data.get("data", [])
        return traces[0] if traces else {}
