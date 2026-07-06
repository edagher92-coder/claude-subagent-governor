"""CLI: python -m subagent_governor "task description" [flags] → JSON decision."""

from __future__ import annotations

import argparse
import json
import sys

from .governor import Decision, Task, classify, escalate, route


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="subagent_governor",
        description="Route one sub-problem to a (model, effort) rung.",
    )
    p.add_argument("description", nargs="?", default="", help="plain-English task")
    p.add_argument("--mechanical", action="store_true")
    p.add_argument("--routine", action="store_true")
    p.add_argument("--deep-narrow", action="store_true")
    p.add_argument("--high-stakes", action="store_true")
    p.add_argument("--architecture", action="store_true")
    p.add_argument("--frontier", action="store_true")
    p.add_argument("--failed", type=int, default=0, metavar="N",
                   help="verification failures so far")
    p.add_argument("--escalate-from", metavar="MODEL/EFFORT",
                   help="return the next rung above e.g. sonnet/high")
    args = p.parse_args(argv)

    if args.escalate_from:
        model, _, effort = args.escalate_from.partition("/")
        decision = escalate(Decision(model, effort, "prior rung"))
    else:
        task = classify(args.description)
        # Explicit flags only ever raise the classification.
        task.mechanical = task.mechanical or args.mechanical
        task.routine = args.routine
        task.deep_narrow = args.deep_narrow
        task.high_stakes = task.high_stakes or args.high_stakes
        task.architecture = task.architecture or args.architecture
        task.frontier = args.frontier
        task.failed_attempts = args.failed
        decision = route(task)

    json.dump(
        {
            "model": decision.model,
            "model_id": decision.model_id,
            "effort": decision.effort,
            "rationale": decision.rationale,
            "transparency": decision.transparency_line(),
        },
        sys.stdout,
        indent=2,
    )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
