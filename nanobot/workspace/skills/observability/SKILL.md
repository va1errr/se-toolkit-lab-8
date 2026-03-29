---
name: observability
description: Use observability MCP tools for logs and traces
always: true
---

# Observability Skill

Use observability MCP tools to investigate system health, errors, and failures.

## Available Tools

- `logs_search` — Search logs using LogsQL query. Returns matching log entries.
- `logs_error_count` — Count errors by service over a time window. Returns total and breakdown.
- `traces_list` — List recent traces. Optionally filter by service name.
- `traces_get` — Fetch a specific trace by ID. Returns full span hierarchy.
- `cron` — Schedule recurring jobs (use for proactive health checks in chat).

## Strategy

### When the user asks "What went wrong?" or "Check system health":

1. Start with `logs_error_count` to see if there are recent errors and which services are affected.
   - Use a narrow time window like "10m" or "2m" for recent issues.
   - If the user specifies a service (e.g., "LMS backend"), filter by that service.

2. If errors are found, use `logs_search` to inspect the actual error messages.
   - Query: `_time:10m severity:ERROR service.name:"Learning Management Service"`
   - Look for `trace_id` fields in the log entries.

3. If you find a `trace_id` in the logs, use `traces_get` to fetch the full trace.
   - This shows the complete request flow and where exactly the failure occurred.

4. Summarize findings concisely:
   - What service is affected
   - What error occurred
   - When it started
   - Impact (how many requests affected)
   - Evidence from both logs AND traces

### When the user asks to create a scheduled health check:

1. Use the `cron` tool to create a recurring job.
2. Each run should:
   - Call `logs_error_count` for the last 2 minutes
   - If errors found, call `logs_search` and optionally `traces_get`
   - Post a short summary to the chat
3. Confirm the job was created by calling `cron({"action": "list"})`.

### When the user asks about scheduled jobs:

1. Call `cron({"action": "list"})` to show all scheduled jobs.
2. To remove a job, call `cron({"action": "remove", "job_id": "..."})`.

### Query patterns:

- **Recent errors in a service**: `_time:10m service.name:"Learning Management Service" severity:ERROR`
- **All errors**: `_time:1h severity:ERROR`
- **Specific event**: `_time:1h event:db_query severity:ERROR`
- **Trace correlation**: `trace_id:<id>` to find all logs for a specific trace

### Response style:

- Keep responses concise and focused on actionable information.
- Don't dump raw JSON — summarize the key findings.
- When showing errors, include: timestamp, service, error message, and trace ID if available.
- If no errors are found in the time window, say so clearly.
- Always cite both log evidence AND trace evidence when investigating failures.

### Example investigation flow:

User: "What went wrong?"

1. Call `logs_error_count(service="Learning Management Service", time_range="10m")`
2. If errors > 0, call `logs_search(query='_time:10m service.name:"Learning Management Service" severity:ERROR')`
3. Extract trace_id from error logs (e.g., "abc123")
4. Call `traces_get(trace_id="abc123")` to see full failure context
5. Summarize: "Found 3 errors in the LMS backend starting at <time>. Logs show <error message>. Trace abc123 shows the failure occurred in <span/service> when <operation> failed."
