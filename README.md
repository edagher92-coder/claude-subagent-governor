# claude-subagent-governor

The enforcement piece of the account's **two-dial subagent routing ladder** —
model (`haiku → sonnet → opus → fable`) × reasoning effort
(`low → medium → high → xhigh → max`). Stdlib-only Python, no config.

Policy sources it codifies (the docs stay canonical; this repo makes them
executable and testable):

- `edagher92-coder/Claude-code-Agents` → `docs/model-routing-policy-v4.md`
- the `/auto-escalate` skill (`edagher92-coder/Claude-code-` →
  `.claude/skills/auto-escalate/`)

Sibling project: `edagher92-coder/claude-model-router` governs **API traffic**
with a live Haiku classifier; this repo governs **Claude Code subagent
spawns** deterministically (no API call to decide).

## What it enforces

- **Quality-first routing:** stakes gate (money / compliance / customer-facing /
  security / architecture) never routes below `opus + high`, even for
  "mechanical" edits.
- **Effort before model** on deep-but-narrow problems (`sonnet + xhigh` before
  `opus + high`).
- **One rung per failure**, never a silent same-config retry; the ladder tops
  out at `fable + max` and then raises `SurfaceToUser` (one fable attempt per
  sub-problem).
- **Mythos is never auto-routable** — constructing a `Decision` for it raises.
- **No self-re-arming loops:** `validate_checkin_interval()` rejects anything
  tighter than one consolidated daily check-in.

## Use

```bash
python -m subagent_governor "grep the repo for TODO markers"
# → {"model": "haiku", "effort": "low", ...}

python -m subagent_governor "process the Merivale refund via Stripe"
# → {"model": "opus", "effort": "high", "rationale": "high-stakes output", ...}

python -m subagent_governor --escalate-from sonnet/high
# → {"model": "sonnet", "effort": "xhigh", ...}
```

```python
from subagent_governor import Task, route, escalate, SurfaceToUser

decision = route(Task(description="fix flaky date parsing", deep_narrow=True))
# spawn Agent(prompt, model=decision.model, effort=decision.effort)
# on failed verification: decision = escalate(decision)
```

Every `Decision` carries `transparency_line()` — the one-line disclosure the
final reply should include, e.g. `escalated: opus/xhigh (root-cause debugging)`.

## Tests

```bash
python -m pytest tests/ -q
```
