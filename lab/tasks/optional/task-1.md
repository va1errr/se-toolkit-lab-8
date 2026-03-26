# Optional — Add a Telegram Bot Client

## Background

The Flutter web client connects to nanobot via the WebSocket channel. A Telegram bot is another client that connects the same way — demonstrating that **the agent is the interface, not any particular frontend**. Same agent, same tools, same answers — different client.

The Telegram bot code is in the `nanobot-websocket-channel` repo you added in Task 2 (at `nanobot-websocket-channel/client-telegram-bot/`). It connects to nanobot via WebSocket and relays messages between Telegram users and the agent. Unlike the web client, you can keep the Telegram bot LMS-specific if you want a `/login` flow there.

### Note on Telegram in Russia

The Telegram Bot API (`api.telegram.org`) is blocked from most Russian servers. Your university VM can't reach it. The bot connects to nanobot via WebSocket (local Docker network — no internet needed for that part), but Telegram polling requires a machine that *can* reach the Bot API. You can either run the bot locally or on a non-Russian server.

## What to do

1. Get a Telegram bot token from [@BotFather](https://t.me/BotFather).

2. Add a `client-telegram-bot` service to `docker-compose.yml`:
   - Build from `nanobot-websocket-channel/client-telegram-bot/`
   - Environment: `BOT_TOKEN`, `NANOBOT_WS_URL=ws://nanobot:8765`
   - `depends_on: nanobot`

3. Deploy and test. Open Telegram, find your bot, and ask it a question.

4. Ask the same question in the Flutter app and in Telegram. Compare — same agent, same answers.

## Acceptance criteria

- The Telegram bot runs as a Docker Compose service (or locally if VM can't reach Telegram API).
- Free-text messages are routed to the agent and responses appear in Telegram.
- The same queries work from both Telegram and the Flutter web app.
