# Onyxia Cyber

Ask Claude about your security program in Onyxia: how your security metrics (CPIs) compare to their SLAs, how they changed over time, and which devices and users are behind them. You can also count and filter your devices and users, or paste a bare value, such as an email address or an IP address, to find out what it belongs to.

For example:

- "Are we inside the SLA for encryption?"
- "How many devices do we have per operating system?"
- `10.20.31.7`

## What it contains

- The Onyxia connector, which reads your Onyxia data. Every tool is read-only.
- Three skills that tell Claude how to answer the way the Onyxia app does: **metrics**, **inventory**, and **lookup**.

## Setup

Installing the plugin does not sign you in. Sign in once with your Onyxia account: on the plugin's Connectors tab in the Claude app, or from `/mcp` in Claude Code. You only see the data your Onyxia account can see.

The full install guide for each Claude surface is at https://github.com/onyxia-cyber/onyxia-claude-plugin#readme.

## Data

The plugin sends Onyxia only your sign-in and the questions Claude asks the Onyxia tools, such as a metric name or a device filter. It reads data from Onyxia and never changes it.

## License

Proprietary. Use only with an active Onyxia subscription. See [LICENSE](LICENSE).
