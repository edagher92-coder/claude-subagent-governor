"""Two-dial subagent routing: model (haiku→sonnet→opus→fable) × effort (low→max).

Quality-first per the house policy: when torn between rungs on quality-relevant
work, round UP. Efficiency comes from tight scoping, never from underpowering.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Auto-routable ladder. Mythos exists but is manual-only by policy — it is
# deliberately NOT in this list, and route() refuses it.
MODELS = ["haiku", "sonnet", "opus", "fable"]
EFFORTS = ["low", "medium", "high", "xhigh", "max"]

MODEL_IDS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-5",
    "opus": "claude-opus-4-8",
    "fable": "claude-fable-5",
}

# Minimum seconds between recurring check-ins. Anything tighter is the
# self-re-arming loop pattern that burned the weekly limit: webhooks or one
# consolidated daily check-in only.
MIN_CHECKIN_SECONDS = 24 * 60 * 60


class SurfaceToUser(Exception):
    """The ladder is exhausted — stop escalating and surface to the user."""


@dataclass
class Task:
    """Attributes of one sub-problem. Flags come from the caller or classify()."""

    description: str = ""
    mechanical: bool = False        # bulk transforms, search, formatting, fan-out
    routine: bool = False           # template-driven judgement, simple edits
    deep_narrow: bool = False       # one gnarly bug/contract: raise effort first
    high_stakes: bool = False       # money / compliance / customer-facing / security
    architecture: bool = False      # multi-system design, ~5+ files, public interface
    frontier: bool = False          # clearly beyond Opus; second-best is a real cost
    failed_attempts: int = 0        # verification failures on prior rungs


@dataclass
class Decision:
    model: str
    effort: str
    rationale: str
    model_id: str = field(init=False)

    def __post_init__(self) -> None:
        if self.model not in MODELS:
            raise ValueError(
                f"model {self.model!r} is not auto-routable (policy: never "
                f"auto-route outside {MODELS})"
            )
        if self.effort not in EFFORTS:
            raise ValueError(f"unknown effort {self.effort!r} (use one of {EFFORTS})")
        self.model_id = MODEL_IDS[self.model]

    def transparency_line(self) -> str:
        """The one-line disclosure the reply should carry."""
        return f"escalated: {self.model}/{self.effort} ({self.rationale})"


# Keyword assist for callers that only have a description. Deterministic and
# deliberately conservative: it can raise flags, never lower them.
_STAKES_RE = re.compile(
    r"\b(refund|charge|invoice|payment|stripe|pricing|price|budget|eofy|tax|ato"
    r"|legal|compliance|contract|security|auth|secret|customer[- ]facing|prod)\b",
    re.I,
)
_MECHANICAL_RE = re.compile(
    r"\b(search|grep|list|inventory|rename|reformat|copy|extract|classify"
    r"|convert|lint)\b",
    re.I,
)
_ARCH_RE = re.compile(r"\b(architect(ure)?|redesign|refactor|migration|api design)\b", re.I)


def classify(description: str) -> Task:
    """Build a Task from a plain-English description (flags only ever raised)."""
    return Task(
        description=description,
        mechanical=bool(_MECHANICAL_RE.search(description)),
        high_stakes=bool(_STAKES_RE.search(description)),
        architecture=bool(_ARCH_RE.search(description)),
    )


def route(task: Task) -> Decision:
    """Initial (model, effort) for a sub-problem, per the two-dial rubric."""
    # Frontier goes straight to the top rung — one attempt, then surface.
    if task.frontier:
        return Decision("fable", "max", "frontier work")

    # Stakes gate overrides cost and mechanical-ness: never below opus/high.
    if task.high_stakes or task.architecture:
        effort = "xhigh" if (task.deep_narrow or task.failed_attempts) else "high"
        why = "high-stakes output" if task.high_stakes else "architecture/design"
        return Decision("opus", effort, why)

    if task.failed_attempts:
        # A failed attempt on an unrouted task starts above the default rung.
        return Decision("opus", "high", f"{task.failed_attempts} failed attempt(s)")

    if task.mechanical:
        return Decision("haiku", "low", "mechanical fan-out")

    if task.routine:
        return Decision("sonnet", "medium", "routine judgement")

    if task.deep_narrow:
        # Effort before model when the problem is deep-but-narrow.
        return Decision("sonnet", "xhigh", "deep-but-narrow: effort before model")

    return Decision("sonnet", "high", "default working tier")


def escalate(prev: Decision, reason: str = "failed verification") -> Decision:
    """One rung up after a failed attempt — never silently retry the same config.

    Deep-but-narrow style first (raise effort within the model), then step the
    model up at high effort. Escalating beyond fable/max raises SurfaceToUser:
    budget is one fable attempt per sub-problem.
    """
    e_i = EFFORTS.index(prev.effort)
    m_i = MODELS.index(prev.model)
    if e_i < EFFORTS.index("xhigh"):
        return Decision(prev.model, EFFORTS[e_i + 1], reason)
    if m_i < len(MODELS) - 1:
        nxt = MODELS[m_i + 1]
        return Decision(nxt, "max" if nxt == "fable" else "high", reason)
    if prev.effort != "max":
        return Decision(prev.model, "max", reason)
    raise SurfaceToUser(
        "fable/max attempt failed — stop escalating and surface to the user"
    )


def validate_checkin_interval(seconds: int) -> int:
    """Reject the self-re-arming check-in loop pattern (< one consolidated daily)."""
    if seconds < MIN_CHECKIN_SECONDS:
        raise ValueError(
            f"check-in every {seconds}s is a self-re-arming loop (policy: webhooks "
            f"or ONE consolidated daily check-in; minimum {MIN_CHECKIN_SECONDS}s)"
        )
    return seconds
