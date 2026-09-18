# Current Task: slack-huddle-leave-off

**Complexity:** Level 1

## Fix

Leave was stuck on-air because `running=true huddle=false inspectable=false ax_windows=0` took the "unreadable / hold" branch. Empty AXWindows is a completed look with no huddle windows, not an unfinished walk.

- Root cause: `slack_huddle.py` held state whenever Slack was running and `inspectable` was false, including zero windows after Leave.
- Change: `observation_kind` returns `clear` for zero AX windows and `hold` only when windows exist but the walk is unreadable. `log_huddle` puts short sentences on info and the field dump on debug.
- Files: `client/toggles/macos/slack_huddle.py`, `client/toggles/macos/test_slack_huddle.py`
- Tests: `python3 -m unittest toggles.macos.test_slack_huddle` from `client/` (7 tests, OK)
