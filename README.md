# Onyxia plugin for Claude

Ask Claude about your security program, using your own Onyxia data. Claude answers the way the Onyxia app does. It only reads your data and never changes anything.

The plugin bundles:

- **The Onyxia connector**, which lets Claude read your security metrics, devices and users.
- **Three skills** that teach Claude to answer like the Onyxia app.

It works in the Claude desktop app, on claude.ai, in Cowork and in Claude Code.

---

## What you can ask

| Skill | What it answers | Try |
| --- | --- | --- |
| **Metrics** | Your security metrics (CPIs) against their SLAs, and how they changed | "Are we inside the SLA for encryption?" |
| **Inventory** | Finding and counting devices and users | "Which laptops are unencrypted?" |
| **Lookup** | What a single value belongs to | Paste `dana@acme.com` or `10.20.31.7` |

---

## Before you start

- An Onyxia account. You see only the data your account can see.
- A Claude Pro, Max, Team or Enterprise plan, or Claude Code.
- The Onyxia client ID, which the Claude app asks for:

  ```text
  50440671-7472-4c72-a3b9-7623d3798903
  ```

## Install

### Claude desktop app or claude.ai

1. Open **Customize > Plugins**, select **Add > Add marketplace**, and enter `https://github.com/onyxia-cyber/onyxia-claude-plugin`.
2. Install **Onyxia Cyber** from the list.
3. On the plugin's **Connectors** tab, add the connector. Pick **Use your own OAuth client**, paste the client ID, leave the secret empty, and save.
   <!-- Screenshot: docs/images/app-connector-dialog.png, the add dialog with "Use your own OAuth client" and the client ID filled in. -->
4. Sign in with your Onyxia account.
   <!-- Screenshot: docs/images/app-sign-in.png, the Onyxia sign-in page opened from Claude. -->

Can't add a marketplace? Download the zip from the [latest release](https://github.com/onyxia-cyber/onyxia-claude-plugin/releases/latest), upload it under **Customize > Plugins > Add > Upload plugin**, then do steps 3 and 4.

### Claude Team or Enterprise

Your Owner sets it up once ([Owner guide](#for-admins)). Then each member:

1. Opens **Customize > Plugins > Onyxia Cyber**, and installs it if it isn't installed yet.
2. Selects **Connect** on the plugin's **Connectors** tab. No client ID needed.
   <!-- Screenshot: docs/images/team-member-connectors.png, the Connectors tab as a member sees it, with Onyxia not connected yet. -->
3. Signs in with their own Onyxia account.

### Claude Code

```bash
claude plugin install onyxia --marketplace onyxia-cyber/onyxia-claude-plugin
```

Then run `/mcp`, choose `plugin:onyxia:onyxia-cyber`, and sign in. The client ID is built in.
<!-- Screenshot: docs/images/code-mcp-sign-in.png, /mcp showing the Onyxia server and the sign-in step. -->

If Claude ever says the connector needs you to sign in, sign in again the same way.
<!-- Renewal not confirmed yet (issue 0002, unknown 4). Once a test shows Claude renews the sign-in by itself, say so here. -->

## Updates

Each release on the [releases page](https://github.com/onyxia-cyber/onyxia-claude-plugin/releases) says what changed.

- **Claude app:** you get new versions when Claude syncs the marketplace. If you uploaded a zip, upload the new one.
- **Claude Code:** run these commands, then restart Claude Code:

  ```bash
  claude plugin marketplace update onyxia
  claude plugin update onyxia@onyxia
  ```

## For admins

<details>
<summary><b>Owner guide</b>: set Onyxia up once for a Claude Team or Enterprise organization</summary>

1. **Add the connector.** In **Organization settings > Connectors**, add a custom connector named `Onyxia Cyber` with the URL `https://mcp.onyxia.io/mcp`. Pick **Use your own OAuth client**, paste the client ID, and leave the secret empty.
   <!-- Screenshot: docs/images/owner-add-connector.png, the organization connector dialog filled in. -->
2. **Add the plugin.** In **Organization settings > Plugins & skills**, select **Add** and upload the zip from the [latest release](https://github.com/onyxia-cyber/onyxia-claude-plugin/releases/latest). Or select **Sync from GitHub** with a private copy of this repo, because Claude syncs an organization's plugins only from a private or internal repo.
3. **Choose who gets it:** **Available** (members choose), **Installed by default** (members can turn it off) or **Required**.
4. **Tell your members** to connect and sign in, as in [Claude Team or Enterprise](#claude-team-or-enterprise).

For each new release, upload the new zip or update your copy of the repo.

</details>

---

## Your data

Onyxia receives your sign-in, through its own sign-in page, and the requests Claude makes, such as a metric name or a device filter. Claude never sees your password. What Onyxia sends back becomes part of your Claude conversation, under your agreement with Anthropic.

## License and help

Proprietary: use only with an active Onyxia subscription. See [the license](plugins/onyxia/LICENSE).

Stuck? Contact Onyxia support and say which step you're on.
