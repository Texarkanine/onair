# Active Context

## Current Task: slack-huddle-leave-off
**Phase:** BUILD - IN-PROGRESS

## What Was Done
- Corrected intent: after Leave the inspector stays at `running=true huddle=false inspectable=false ax_windows=0` and the toggle holds on-air.
- Classified Level 1: bug fix in a single component (macOS Slack huddle toggle), plus matching info/debug log split.

## Next Step
- Locate root cause, write a failing test, then fix hold-on-empty-windows and info/debug logging.
