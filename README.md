# Onyxia plugin for Claude

This plugin connects Claude to Onyxia, so Claude can read your organization's security metrics, devices and users, and answer questions about them. You need an Onyxia active account to use it.

Ask Claude about your security program in Onyxia:

- "Are we inside the SLA for encryption?"
- "How did MFA coverage change since July?"
- "How many devices do we have per operating system?"
- Paste a bare value, such as `dana@acme.com` or `10.20.31.7`, to find out what it belongs to.

Claude answers from your own Onyxia data, the way the Onyxia app does. The plugin works in the Claude desktop app, on claude.ai, in Cowork and in Claude Code.

## What you need

- An Onyxia account. You only see the data your Onyxia account can see.
- A Claude Pro, Max, Team or Enterprise plan, or Claude Code.
- Onyxia client ID:
  
  ```text
  50440671-7472-4c72-a3b9-7623d3798903
  ```

## Install

Pick the section for how you use Claude. Every section has two parts: install the plugin once, then sign in once.

### Claude desktop app or claude.ai, for yourself

1. Open **Customize > Plugins**, select **Add**, then **Add marketplace**.
2. Enter `https://github.com/onyxia-cyber/onyxia-claude-plugin` and add it.
3. Find **Onyxia Cyber** in the list and install it.
4. Open the Onyxia Cyber plugin and go to its **Connectors** tab. The connector shows **Not added**. Select it to add it.
5. In the dialog, open the OAuth client choice and pick **Use your own OAuth client**. Paste the client ID from [What you need](#what-you-need). Leave the secret empty. Save.
   <!-- Screenshot: docs/images/app-connector-dialog.png, the add dialog with "Use your own OAuth client" and the client ID filled in. -->
6. Sign in with your Onyxia account on the page that opens.
   <!-- Screenshot: docs/images/app-sign-in.png, the Onyxia sign-in page opened from Claude. -->
7. The connector now shows **Connected**. Ask Claude an Onyxia question.

**Cannot add a marketplace?**

Download the zip from the [latest release](https://github.com/onyxia-cyber/onyxia-claude-plugin/releases/latest). 
In **Customize > Plugins**, select **Add**, then **Upload plugin**, and choose the zip. Then follow steps 4 to 7.

### Claude Team or Enterprise

An Owner sets Onyxia up once for the organization. Each member then signs in with their own Onyxia account.

**What the Owner does once.** See the [Owner guide](#owner-guide) below.

**What each member does.**

1. Open **Customize > Plugins** and open **Onyxia Cyber**. If it is only available, not installed, install it.
2. Go to the plugin's **Connectors** tab and select **Connect** next to Onyxia Cyber. You do not need the client ID; the Owner already added it.
   <!-- Screenshot: docs/images/team-member-connectors.png, the Connectors tab as a member sees it, with Onyxia not connected yet. -->
3. Sign in with your own Onyxia account.
4. The connector shows **Connected**. Ask Claude an Onyxia question.

### Claude Code

1. Install the plugin with one command in your terminal:

   ```bash
   claude plugin install onyxia --marketplace onyxia-cyber/onyxia-claude-plugin
   ```

   Or, inside Claude Code:

   ```text
   /plugin marketplace add onyxia-cyber/onyxia-claude-plugin
   /plugin install onyxia@onyxia
   ```

2. Start Claude Code, run `/mcp`, choose `plugin:onyxia:onyxia_cyber`, and sign in. The client ID is already in the plugin, so you do not type it.
   <!-- Screenshot: docs/images/code-mcp-sign-in.png, /mcp showing the Onyxia server and the sign-in step. -->
3. Your browser opens the Onyxia sign-in page. Sign in. The browser then returns to `http://localhost:41871/callback` on your own machine, and Claude Code finishes the sign-in.
4. Ask Claude an Onyxia question.

If you installed the plugin on claude.ai, Claude Code gets it too, at the start of your next session.

## Signing in

Installing the plugin does not sign you in. Until you sign in, Onyxia refuses every request, and Claude tells you the connector needs you to sign in. Sign in once, as in the steps above. Claude keeps you signed in and renews your sign-in in the background, so you are not asked again on every question.
<!-- DRAFT: confirm renewal in the sign-in spike (issue 0002, unknown 4) before release. -->

## Updates

New versions bring better answers. A release note on the [releases page](https://github.com/onyxia-cyber/onyxia-claude-plugin/releases) says what changed.

- **Claude desktop app and claude.ai:** you get the new version when Claude next syncs the marketplace. For a zip upload, upload the new zip.
- **Claude Code:** plugins from this marketplace do not update on their own. When a release note appears, run:
  
  ```bash
  claude plugin marketplace update onyxia
  claude plugin update onyxia@onyxia
  ```
  
  Restart Claude Code.

## Owner guide

For the Owner of a Claude Team or Enterprise organization. It takes a few minutes.

1. **Add the connector for everyone.** Go to **Organization settings > Connectors** and add a custom connector:
   - Name: `Onyxia Cyber`
   - URL: `https://api.onyxia.io/mcp`
   - OAuth client: **Use your own OAuth client**, with the client ID from [What you need](#what-you-need) and no secret.
     <!-- Screenshot: docs/images/owner-add-connector.png, the organization connector dialog filled in. -->
2. **Add the plugin for the organization**, in **Organization settings > Plugins & skills**, in one of two ways:
   - Select **Add**, then upload the zip from the [latest release](https://github.com/onyxia-cyber/onyxia-claude-plugin/releases/latest). Upload the new zip for each new release.
   - Or keep a private copy of this repository in your organization's GitHub and select **Add**, then **Sync from GitHub**, with that copy. Claude can sync an organization's marketplace only from a private or internal repository. Update the copy from this repository for each new release.
3. **Choose who gets it.** Set the Onyxia Cyber plugin to **Available** (members install it themselves), **Installed by default** (members have it and can turn it off) or **Required** (members cannot turn it off).
4. **Tell your members** to open the plugin's **Connectors** tab and sign in with their Onyxia account, as in [Claude Team or Enterprise](#claude-team-or-enterprise).

## Claude Code admin guide

For administrators who manage Claude Code across an organization. Managed settings can add the Onyxia marketplace and install the plugin on every machine, with nothing for developers to do. Add these keys to your managed settings, whether server-managed settings in **Organization settings > Claude Code > Managed settings**, an MDM policy, or a `managed-settings.json` file:

```json
{
  "extraKnownMarketplaces": {
    "onyxia": {
      "source": { "source": "github", "repo": "onyxia-cyber/onyxia-claude-plugin" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "onyxia@onyxia": true
  },
  "permissions": {
    "allow": ["mcp__plugin_onyxia_onyxia_cyber"]
  }
}
```

The plugin installs at the start of each developer's next session. `"autoUpdate": true` keeps it up to date in the background, so developers do not need the update commands. The `permissions` rule lets Claude Code use every Onyxia tool without asking each time. All of them only read data. Each developer still signs in once from `/mcp`.

## What data goes to Onyxia

- Your sign-in, through Onyxia's own sign-in page. Claude never sees your password.
- The requests Claude makes to the Onyxia tools, such as a metric name, a device filter, or a value you asked about.

The Onyxia tools only read data. They never change anything in Onyxia. What Onyxia sends back to Claude, such as metric values, device names and people's names, becomes part of your Claude conversation and is handled under your agreement with Anthropic.

## License

Proprietary: use only with an active Onyxia subscription. No copying, modification or redistribution. See [the license](plugins/onyxia/LICENSE).

## Help

Contact Onyxia support, and name the section and step where you are stuck.
