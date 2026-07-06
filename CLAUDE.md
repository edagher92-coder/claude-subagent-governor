# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## Repository purpose

> **Inferred, not confirmed.** This repo currently contains only a LICENSE file
> and a `.gitignore` — there is no README, no code, and no commit history beyond
> "Add MIT License" and "Add Python .gitignore". Nothing in the repo states its
> purpose yet. The paragraph below is a **guess derived from the repo name**,
> read against sibling repos already in this account
> (`edagher92-coder/skill_router`, `edagher92-coder/claude-model-router`). Treat
> it as a proposal to validate with the owner (Elie Dagher) before building
> against it, not as documented fact.
>
> Working name **"claude-subagent-governor"** plausibly suggests a tool that
> **governs Claude Code subagent usage** — e.g. enforcing which model/effort
> tier a delegated task is allowed to run at, capping how many subagents or
> babysitter sessions run concurrently, or gating subagent tool permissions —
> in the same spirit as the account-wide token-efficiency rules in
> `edagher92-coder/.github/CLAUDE.md` (model routing via `/auto-escalate`, "one
> babysitter session max", no self-re-arming check-in loops). It would likely
> sit alongside `skill_router` (routes a query to the right skill) and
> `claude-model-router` (the model-routing policy doc/source of truth) as a
> third piece of infrastructure, but this time enforcing/auditing subagent
> behavior rather than choosing a skill or a model tier. **None of this is
> implemented or confirmed — confirm scope with the owner before writing code
> against this assumption.**

> **Status: the repository is in its initial state.** This file documents the
> intended structure and conventions, adapted from the same template used for
> `edagher92-coder/Claude-code-Agents` at its own initial-state point; folders
> should be created as content is added. Update this file whenever the
> conventions change or the real purpose is confirmed.

## Suggested layout

Create directories on demand — don't pre-create empty ones.

```
agents/      Subagent definitions (one Markdown file per agent, YAML frontmatter
             with name/description/tools, body is the system prompt).
skills/      Skills — each skill is its own directory containing a SKILL.md
             plus any helper scripts or reference files it loads.
commands/    Custom slash commands (Markdown files; filename becomes the
             /command-name).
hooks/       Hook scripts invoked by settings.json (SessionStart, PreToolUse,
             PostToolUse, Stop, etc.). Keep them small and POSIX-portable
             unless a specific runtime is required.
settings/    Reusable settings.json snippets, plus any merge/install scripts.
docs/        Long-form notes that don't belong in a single agent/skill file —
             e.g. the eventual write-up of what "governor" actually means here.
```

If the confirmed purpose turns out to be a policy/enforcement layer rather than
agents+skills, this layout should be revisited — don't force content into these
directories just because the template suggests them.

## Authoring conventions

### Agents (`agents/<name>.md`)

- Frontmatter: `name`, `description` (written so the orchestrator knows *when*
  to delegate), and optional `tools` (comma-separated allow-list; omit to
  inherit the parent's tools).
- The description is the routing signal — lead with the trigger ("Use when…"),
  not a feature list.
- Body is the agent's system prompt. Treat the agent as stateless: every
  invocation starts fresh, so the prompt must carry all the context the agent
  needs.

### Skills (`skills/<name>/SKILL.md`)

- Frontmatter: `name`, `description`. The description follows the same
  trigger-first style as agents.
- Keep `SKILL.md` short; offload long reference material to sibling files the
  skill instructs Claude to read on demand.
- Helper scripts live alongside `SKILL.md` in the same directory.

### Slash commands (`commands/<name>.md`)

- Filename (without `.md`) becomes the command, e.g. `commands/review.md` →
  `/review`.
- Use `$ARGUMENTS` (or `$1`, `$2`, …) to inject user input.
- Optional frontmatter: `description`, `argument-hint`, `allowed-tools`.

### Hooks (`hooks/<event>/<name>.sh`)

- One script per concern; chain them in `settings.json` rather than building a
  monolith.
- Exit code 0 = allow; exit code 2 on `PreToolUse` = block with the stderr
  message surfaced to Claude. Document any non-obvious exit codes inline.
- Read the hook event JSON from stdin; don't rely on positional arguments.

### Settings (`settings/`)

- Prefer minimal diffs against the user's existing `~/.claude/settings.json`.
- When a setting only makes sense paired with a hook or command in this repo,
  reference that path relatively (e.g. `${CLAUDE_PROJECT_DIR}/hooks/...`) so
  the snippet is portable.

## Planned work

- [ ] Confirm the repo's actual purpose with the owner and replace the
      "Repository purpose" section above with a factual description once
      confirmed.
- [ ] Wire up validation tooling (linter/formatter) once real content exists;
      fill in the `tests` / `lint` / `format` placeholders under
      [Local validation](#local-validation).
- [ ] If the "governor" concept is confirmed, decide how it relates to
      `skill_router` and `claude-model-router` — shared code vs. a thin
      policy layer that calls into them.

## Local validation

There is no test suite or linter configured yet. When that changes, add the
commands here so future sessions know how to validate changes:

```
# tests:   <not configured>
# lint:    <not configured>
# format:  <not configured>
```

## Workflows

### Adding a new agent / skill / command

1. Create the file in the right directory using the conventions above.
2. Test it locally — for agents, invoke via `Task`/subagent; for skills, run
   the trigger phrase; for commands, type the slash command.
3. Commit with a message that names the artifact: `add agents/<name>`,
   `update skills/<name>: <change>`, etc.

### Branching & PRs

- Default branch: `main`.
- Feature branches: `claude/<short-slug>` for AI-generated work, free-form for
  human work.
- All pushes from Claude Code on the web open a **draft** PR automatically.

## House rules for Claude

- **Follow the account-wide father rule first:** `edagher92-coder/.github/CLAUDE.md`
  applies in every repo under this account, including this one — default
  model is Sonnet with deliberate escalation via `/auto-escalate`, no
  self-re-arming check-in loops, PR monitoring is webhook-subscription only,
  one babysitter session max, fresh session per task over resuming a huge old
  one, and no Claude-in-CI on cron without an explicit budget decision. Read
  it before setting up any automation in this repo.
- Don't pre-create empty scaffolding directories — add them when there's
  actual content to put in them.
- Don't invent agents, skills, or commands that the user hasn't asked for,
  and don't implement the "subagent governor" concept described above as if
  it were confirmed — it is a name-derived guess pending owner sign-off.
- When editing an existing agent/skill/command, preserve its frontmatter
  structure exactly; only change fields the task requires.
- Update this `CLAUDE.md` whenever a convention changes, a new top-level
  directory is introduced, tooling (tests/lint/format) is added, or the real
  purpose of the repo is confirmed.
