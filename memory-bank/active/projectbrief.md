# Project Brief

## User Story

As someone using the macOS Slack huddle toggle, I want the sign to go off-air when I leave a huddle, and I want info logs I can read at a glance, so the detector matches real huddle state without dumping inspection fields at info.

## Use-Case(s)

### Use-Case 1

I join a Slack huddle. The toggle goes on-air. I click Leave in the huddle window and that window goes away. Slack is still running. The inspector reports `running=true`, `huddle=false`, `inspectable=false`, `ax_windows=0`. The toggle must go off-air (after the existing stop hysteresis), not hold the previous on-air state.

### Use-Case 2

While the toggle is polling, info-level log lines stay short and human-readable, in the same style as the other macOS toggles. The long field dump (`running=… huddle=… inspectable=… ax_windows=…` plus hysteresis counters) is logged at debug.

## Requirements

1. After Leave, the `running=true huddle=false inspectable=false ax_windows=0` observation must count toward ending the huddle, not toward holding on-air.
2. Existing start/stop hit thresholds stay in place.
3. Info logs are short human-readable sentences. Long inspector/hysteresis data is debug.

## Constraints

1. Scope is the macOS Slack huddle toggle.
2. Do not activate Slack.

## Acceptance Criteria

1. From on-air, repeated `running=true huddle=false inspectable=false ax_windows=0` observations reach the stop threshold and call the callback with `False`.
2. Info-level huddle log lines do not include the long field dump; that dump appears at debug.
