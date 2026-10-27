# Changes

Claude Code users: plugins from this marketplace do not update on their own. After a new release, run:

```bash
claude plugin marketplace update onyxia
claude plugin update onyxia@onyxia
```

## 0.1.1 (2026-10-27)

- The plugin has a logo, used for its listing in Anthropic's directory.
- The connector key is now `onyxia-cyber` instead of `onyxia_cyber`. In Claude Code the server is `plugin:onyxia:onyxia-cyber`, and permission rules use `mcp__plugin_onyxia_onyxia-cyber`.

## 0.1.0 (2026-10-27)

The first release.

- The Onyxia connector at `https://api.onyxia.io/mcp`, with read-only tools for metrics, devices, users and connected products.
- Three skills, the same ones the Onyxia assistant Nexa uses: **metrics** for CPIs, SLAs and trends, **inventory** for counting and finding devices and users, and **lookup** for a bare value such as an email or IP address.
