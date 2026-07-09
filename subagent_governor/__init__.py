"""Subagent governor — the enforcement piece of the two-dial routing ladder.

Codifies docs/model-routing-policy-v4.md (edagher92-coder/Claude-code-Agents)
and the /auto-escalate skill: given a sub-problem's attributes, return the
(model, effort) rung to spawn a subagent at, escalate one rung after a failed
attempt, and hard-block the patterns the account bans (Mythos auto-routing,
self-re-arming check-in loops).
"""

from .governor import (
    EFFORTS,
    MODELS,
    Decision,
    SurfaceToUser,
    Task,
    classify,
    escalate,
    route,
    validate_checkin_interval,
)

__all__ = [
    "MODELS",
    "EFFORTS",
    "Task",
    "Decision",
    "SurfaceToUser",
    "route",
    "escalate",
    "classify",
    "validate_checkin_interval",
]
