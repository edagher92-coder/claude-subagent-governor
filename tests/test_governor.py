import pytest

from subagent_governor import (
    Decision,
    SurfaceToUser,
    Task,
    classify,
    escalate,
    route,
    validate_checkin_interval,
)


def test_mechanical_routes_to_haiku_low():
    d = route(Task(mechanical=True))
    assert (d.model, d.effort) == ("haiku", "low")


def test_default_is_sonnet_high():
    d = route(Task())
    assert (d.model, d.effort) == ("sonnet", "high")


def test_routine_is_sonnet_medium():
    d = route(Task(routine=True))
    assert (d.model, d.effort) == ("sonnet", "medium")


def test_deep_narrow_raises_effort_before_model():
    d = route(Task(deep_narrow=True))
    assert (d.model, d.effort) == ("sonnet", "xhigh")


def test_stakes_gate_overrides_mechanical():
    # A "mechanical" pricing edit is still money-touching: never below opus.
    d = route(Task(mechanical=True, high_stakes=True))
    assert d.model == "opus"
    assert d.effort in ("high", "xhigh")


def test_frontier_goes_straight_to_fable_max():
    d = route(Task(frontier=True))
    assert (d.model, d.effort) == ("fable", "max")


def test_failed_attempt_starts_above_default():
    d = route(Task(failed_attempts=1))
    assert (d.model, d.effort) == ("opus", "high")


def test_escalate_never_repeats_the_same_rung():
    d = Decision("sonnet", "high", "start")
    seen = {(d.model, d.effort)}
    while True:
        try:
            d = escalate(d)
        except SurfaceToUser:
            break
        assert (d.model, d.effort) not in seen
        seen.add((d.model, d.effort))
    assert ("fable", "max") in seen


def test_escalate_raises_effort_within_model_first():
    d = escalate(Decision("sonnet", "high", "start"))
    assert (d.model, d.effort) == ("sonnet", "xhigh")


def test_fable_max_failure_surfaces_to_user():
    with pytest.raises(SurfaceToUser):
        escalate(Decision("fable", "max", "frontier"))


def test_mythos_is_never_auto_routable():
    with pytest.raises(ValueError):
        Decision("mythos", "high", "nope")


def test_classify_flags_stakes_and_mechanical():
    assert classify("process the Merivale refund via Stripe").high_stakes
    assert classify("grep the repo for TODO markers").mechanical
    assert classify("EOFY tax caption copy").high_stakes


def test_classify_never_lowers_default():
    d = route(classify("write a poem about slushies"))
    assert (d.model, d.effort) == ("sonnet", "high")


def test_checkin_interval_blocks_hourly_loops():
    with pytest.raises(ValueError):
        validate_checkin_interval(3600)
    assert validate_checkin_interval(86400) == 86400
