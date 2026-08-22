# Score Submission Bot Options

Comparison of messaging bots as alternatives to the web form for submitting
scores to the Quaranta Crediti leaderboard.

## The architecture (same for all bots)

```
Message → Bot → GitHub Issue → score-update.yml → site updates
```

The bot just creates issues in the format the workflow already expects.
No changes to the existing pipeline.

---

## Telegram

- **API**: Official Bot API, free, no costs
- **Setup**: Trivial — create bot via @BotFather, get a token, set a webhook
- **Self-hosting**: No — Telegram hosts the bot infrastructure
- **Open source**: Client is open source (Telegram clients), server is not
- **Phone number**: Not required for the bot (just @BotFather)
- **Text + photos**: Native support for both
- **Webhook support**: Yes — Telegram sends updates to your endpoint
- **Hosting for webhook**: Cloudflare Worker (free), Vercel Edge (free), or any
  small serverless function
- **Example message format**:
  ```
  /pooyan 79000
  moon patrol 120000
  ```
- **Photo handling**: User sends photo with the message, bot downloads it and
  attaches it to the issue body
- **Latency**: Instant (webhook-based)
- **Pros**: Simplest option, free, reliable, well-documented, huge community
- **Cons**: Proprietary server (though client is open source)

## Signal

- **API**: No official bot API — uses signal-cli + REST API wrapper
- **Setup**: Moderate — requires several components:
  1. A dedicated phone number for the bot account
  2. signal-cli-rest-api running in Docker (https://github.com/bbernhard/signal-cli-rest-api)
  3. A bot framework on top (signalbot, cygnet, or signal-sdk)
  4. A server to run everything
- **Self-hosting**: Yes — everything is self-hosted
- **Open source**: Fully open source (signal-cli, signal-cli-rest-api, bot frameworks)
- **Phone number**: Required to register a Signal account for the bot
- **Text + photos**: Supported via the REST API
- **Webhook support**: Yes — signal-cli-rest-api supports webhooks
- **Hosting**: VPS, home server, or any Docker-capable host
- **Bot frameworks**:
  - signalbot (Python, MIT) — https://github.com/signalbot-org/signalbot
  - cygnet (TypeScript, MIT) — https://github.com/sudodaksh/cygnet
  - signal-sdk (TypeScript, MIT) — https://github.com/benoitpetit/signal-sdk
- **Latency**: Near-instant (webhook or WebSocket)
- **Pros**: Fully open source, end-to-end encrypted, privacy-first
- **Cons**: More complex setup, requires a phone number, Docker management,
  must keep the server alive

## WhatsApp

- **API**: Meta Cloud API (Business)
- **Setup**: Moderate to complex:
  1. Meta Business account verification
  2. Phone number registration
  3. App review process
- **Self-hosting**: No — uses Meta's cloud API
- **Open source**: No — proprietary, closed platform
- **Phone number**: Required (business account)
- **Text + photos**: Supported
- **Costs**: First 1000 conversations/month free, then $0.00–$0.05/conversation
- **Latency**: Near-instant
- **Pros**: Huge user base, everyone has it
- **Cons**: Business verification required, costs after free tier,
  proprietary, restrictive terms of service, less developer-friendly

## Discord

- **API**: Official bot API, free
- **Setup**: Easy — create app at discord.com/developers, get a token, invite bot
- **Self-hosting**: No — Discord hosts the bot infrastructure
- **Open source**: No — proprietary platform
- **Phone number**: Not required
- **Text + files**: Supported (bots can receive messages and attachments)
- **Webhook support**: Yes — interactions and messages via gateway or webhooks
- **Hosting**: Bot runs locally or on a server; gateway connection needed
- **Latency**: Near-instant (WebSocket gateway)
- **Pros**: Easy setup, good API, free
- **Cons**: Not open source, gamery vibe, requires gateway connection (not pure webhook)

---

## Summary

| Feature         | Telegram      | Signal           | WhatsApp    | Discord     |
|-----------------|---------------|------------------|-------------|-------------|
| Setup           | Trivial       | Moderate         | Moderate    | Easy        |
| Self-hosting    | No            | Yes (Docker)     | No          | No          |
| Open source     | Client only   | Fully            | No          | No          |
| Phone required  | No            | Yes              | Yes (biz)   | No          |
| Costs           | Free          | Free             | Paid tier   | Free        |
| Photo support   | Yes           | Yes              | Yes         | Yes         |
| Latency         | Instant       | Near-instant     | Near-instant| Instant     |

## Recommendation

- **Simplest**: Telegram — free, 5-minute setup, no server to maintain
- **Most open**: Signal — fully open source, but requires Docker + phone number
- **Skip**: WhatsApp (costs, verification, proprietary) and Discord (not open source,
  wrong vibe for a retro arcade site)
