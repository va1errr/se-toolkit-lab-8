---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

Use LMS MCP tools to answer questions about the Learning Management System.

## Available Tools

- `lms_health` — Check if the LMS backend is healthy and report the item count. No arguments needed.
- `lms_labs` — List all labs available in the LMS. Returns lab identifiers and titles. No arguments needed.
- `lms_learners` — List all learners registered in the LMS. No arguments needed.
- `lms_pass_rates` — Get pass rates (avg score and attempt count per task) for a specific lab. Requires `lab` parameter.
- `lms_timeline` — Get submission timeline (date + submission count) for a specific lab. Requires `lab` parameter.
- `lms_groups` — Get group performance (avg score + student count per group) for a specific lab. Requires `lab` parameter.
- `lms_top_learners` — Get top learners by average score for a specific lab. Requires `lab` and optional `limit` (default 5).
- `lms_completion_rate` — Get completion rate (passed / total) for a specific lab. Requires `lab` parameter.
- `lms_sync_pipeline` — Trigger the LMS sync pipeline. Use when data seems stale or user asks to refresh. No arguments needed.

## Strategy

### When the user asks about scores, pass rates, completion, groups, timeline, or top learners without naming a lab:

1. Call `lms_labs` first to get the list of available labs.
2. If multiple labs are available, use the `mcp_webchat_ui_message` tool with `type: "choice"` to let the user pick a lab.
   - Use each lab's `title` field as the user-facing label.
   - Use the lab's `id` field as the value to pass back.
   - Include the current `chat_id` from runtime context.
3. Once the user selects a lab, call the appropriate tool with the selected lab identifier.

### When the user asks which lab has the lowest/highest pass rate or similar comparison:

1. Call `lms_labs` to get all labs.
2. Call `lms_pass_rates` for each lab.
3. Compare the results and answer with the lab that matches the criteria.

### When the user asks about system health or if the backend is working:

1. Call `lms_health` to check the backend status.
2. Report whether it's healthy and mention the item count.

### When lab parameter is needed but not provided:

- Always ask the user to specify which lab they mean.
- Use `lms_labs` first if you don't know the available labs.
- Present choices using `mcp_webchat_ui_message` on supported channels, or plain text in CLI.

### Formatting numeric results:

- Display percentages with one decimal place (e.g., "75.3%").
- Display counts as whole numbers.
- For completion rate, show both the fraction and percentage (e.g., "12/20 learners (60%)").

## Response Style

- Keep responses concise and focused on the data requested.
- When presenting tool results, summarize key findings rather than dumping raw JSON.
- If a tool returns an error, explain what went wrong in plain language.
- When the user asks "what can you do?", explain that you can query the LMS for:
  - Available labs
  - Pass rates and scores per lab
  - Top learners in a lab
  - Group performance
  - Submission timelines
  - Completion rates
  - Backend health status
  - Triggering the sync pipeline
