#!/usr/bin/env python3
"""Entrypoint for nanobot Docker container.

Resolves environment variables into config.json at runtime,
then execs into `nanobot gateway`.
"""

import json
import os
import shutil
import sys
from pathlib import Path


def main():
    config_dir = Path(__file__).parent
    config_path = config_dir / "config.json"
    # Write resolved config to /tmp since the source directory might be read-only in Docker
    resolved_path = Path("/tmp/config.resolved.json")
    
    # Workspace is mounted at /app/nanobot-src/workspace but we need to initialize it from the image
    workspace_dir = Path("/app/nanobot-src/workspace")
    workspace_template = Path("/app/workspace-template")
    
    # Copy workspace template if workspace is empty (first run)
    if workspace_dir.exists() and not list(workspace_dir.iterdir()):
        if workspace_template.exists():
            shutil.copytree(workspace_template, workspace_dir, dirs_exist_ok=True)
    elif not workspace_dir.exists():
        if workspace_template.exists():
            shutil.copytree(workspace_template, workspace_dir)
        else:
            workspace_dir.mkdir(parents=True, exist_ok=True)

    # Read base config
    with open(config_path) as f:
        config = json.load(f)

    # Override provider settings from env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base_url = os.environ.get("LLM_API_BASE_URL")
    llm_api_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_api_base_url:
        config["providers"]["custom"]["apiBase"] = llm_api_base_url
    if llm_api_model:
        config["agents"]["defaults"]["model"] = llm_api_model

    # Override gateway settings from env vars
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")

    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)

    # Configure webchat channel if enabled via env
    webchat_enabled = os.environ.get("NANOBOT_WEBCHAT_ENABLED", "false").lower() == "true"
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "0.0.0.0")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")

    if webchat_enabled or webchat_port:
        config["channels"]["webchat"] = {
            "enabled": True,
            "host": webchat_host,
            "port": int(webchat_port) if webchat_port else 8765,
            "allowFrom": ["*"],
        }

    # Configure MCP servers from env vars
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")
    victorialogs_url = os.environ.get("NANOBOT_VICTORIALOGS_URL")
    victoriatraces_url = os.environ.get("NANOBOT_VICTORIATRACES_URL")
    webchat_relay_url = os.environ.get("NANOBOT_WEBCHAT_RELAY_URL")
    webchat_token = os.environ.get("NANOBOT_WEBCHAT_TOKEN")

    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}

    # LMS MCP server
    if lms_backend_url or lms_api_key:
        config["tools"]["mcpServers"]["lms"] = {
            "command": "python",
            "args": ["-m", "mcp_lms"],
            "env": {},
        }
        if lms_backend_url:
            config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
        if lms_api_key:
            config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Observability MCP server
    if victorialogs_url or victoriatraces_url:
        config["tools"]["mcpServers"]["observability"] = {
            "command": "python",
            "args": ["-m", "mcp_obs"],
            "env": {},
        }
        if victorialogs_url:
            config["tools"]["mcpServers"]["observability"]["env"]["NANOBOT_VICTORIALOGS_URL"] = victorialogs_url
        if victoriatraces_url:
            config["tools"]["mcpServers"]["observability"]["env"]["NANOBOT_VICTORIATRACES_URL"] = victoriatraces_url

    # Webchat MCP server for structured UI messages
    if webchat_relay_url or webchat_token:
        config["tools"]["mcpServers"]["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {},
        }
        if webchat_relay_url:
            config["tools"]["mcpServers"]["webchat"]["env"]["NANOBOT_WEBCCHAT_RELAY_URL"] = webchat_relay_url
        if webchat_token:
            config["tools"]["mcpServers"]["webchat"]["env"]["NANOBOT_WEBCCHAT_TOKEN"] = webchat_token
    elif webchat_enabled or webchat_port:
        # Enable webchat MCP server with default config when webchat channel is enabled
        config["tools"]["mcpServers"]["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {
                "NANOBOT_WEBCCHAT_RELAY_URL": f"ws://{webchat_host}:{webchat_port if webchat_port else 8765}",
                "NANOBOT_WEBCCHAT_TOKEN": os.environ.get("NANOBOT_ACCESS_KEY", ""),
            },
        }

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    # Exec into nanobot gateway
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(resolved_path),
            "--workspace",
            str(workspace_dir),
        ],
    )


if __name__ == "__main__":
    main()
