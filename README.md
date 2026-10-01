# Ninepigs for agents

[Ninepigs](https://ninepigs.com) keeps a household's shared money: what its members earn and spend,
what they plan to, and what they save. This repository is what an AI agent needs to run it for you:
the **skill** that teaches an agent the routine, and the install steps for each agent. The agent
works on your household's live books through Ninepigs' MCP server, with a token you create and can
revoke at any time.

What the skill does, once installed:

- **The period routine.** Import your banks' CSV exports, let the app settle what it is sure of,
  review the rest with your household's own conventions and precedents, record it, check that
  nothing is unrecorded, close the period and open the next.
- **Money questions.** How much is left, what was that charge, how a fund is doing, what is due.
- **Keeping plans current.** Bills that changed, new subscriptions, budgets, savings goals.
- **Learning your household.** Which bank accounts each Ninepigs account stands for, who the
  e-transfer counterparties are, which stores go to whose fund — kept as *household notes* in the
  app, so every member's agent reads the same ones.

The agent decides nothing the app could not: it never guesses a category from merchant text, it
asks you about anything the precedents do not settle, and it previews writes before making them.

## Install

Two steps for any agent: connect it to your household, and give it the skill.

### 1. Connect

Create a token in Ninepigs under **Settings → Security → API tokens**. Name it after the agent and
pick a scope:

| Scope | What the agent can do |
|---|---|
| `read` | answer questions |
| `record` | also import statements and record money, but change nothing |
| `write` | also keep the notes, schedules, funds and periods current |

Hosted agents (Claude.ai, ChatGPT) connect through OAuth instead and ask for the scope on the way.

### 2. Install the skill

| Agent | Skill | Connection |
|---|---|---|
| **Claude Code** | `claude plugin marketplace add bo2dev/ninepigs` then `claude plugin install ninepigs@ninepigs` | the plugin asks for your token and connects the MCP server itself |
| **Codex** | `$skill-installer bo2dev/ninepigs/skills/ninepigs` | `codex mcp add ninepigs --url https://api.ninepigs.com/mcp --bearer-token-env-var NINEPIGS_API_TOKEN`, with the token exported in your shell |
| **Claude.ai, Claude desktop** | download `ninepigs-skill.zip` from the latest [release](https://github.com/bo2dev/ninepigs/releases) and add it under Settings → Capabilities → Skills | add a custom connector at `https://api.ninepigs.com/mcp` |
| **ChatGPT** | import the `skills/ninepigs` folder from this repository (Create → Upload) | add `https://api.ninepigs.com/mcp` as a custom MCP connector in developer mode |

Check it works: start a new session and ask "What's my household's currency?". The agent answers
from your books.

### Without an MCP connection

A headless job or an agent with no MCP client can call the API directly with
[`skills/ninepigs/scripts/ninepigs.py`](skills/ninepigs/scripts/ninepigs.py) (Python 3, no
dependencies, token in `NINEPIGS_API_TOKEN`). The API reference is at
[ninepigs.com/docs/api](https://ninepigs.com/docs/api).

## Keep it safe

- Treat the token like a password; revoke it in Settings → Security to disconnect an agent at once.
- Give each agent its own token, so revoking one does not disconnect the rest.
- Writes land in your books immediately, for the whole household to see. The skill confirms
  amounts, dates and destinations with you before recording; if an agent does not, ask it to.
- The household notes are yours: read and correct them in the app under your household settings.

## Versions

The skill's version (`metadata.version` in `SKILL.md`) is this repository's release tag. The app
reports the version it was tested against in `get_context`; an installed skill that reads a
different one tells you to update. See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE). The skill and the client script are open; Ninepigs itself is a separate,
proprietary product.
