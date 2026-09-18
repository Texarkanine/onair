# Current Task: slack-huddle-leave-off

**Complexity:** Level 1

## Fix

Leave was stuck on-air because `running=true huddle=false inspectable=false ax_windows=0` took the "unreadable / hold" branch. Empty AXWindows is a completed look with no huddle windows, not an unfinished walk.

- Root cause: `slack_huddle.py` held state whenever Slack was running and `inspectable` was false, including zero windows after Leave.
- Change: `observation_kind` returns `clear` for zero AX windows and `hold` only when windows exist but the walk is unreadable. `log_huddle` puts short sentences on info and the field dump on debug.
- Files: `client/toggles/macos/slack_huddle.py`, `client/toggles/macos/test_slack_huddle.py`
- Tests: `python3 -m unittest toggles.macos.test_slack_huddle` from `client/` (7 tests, OK)

## QA Results

- PASS (2026-09-18). Semantic review against the brief found no blocking issues.
- Classifier matches inspector semantics: `inspectable=false ax_windows=0` is a completed look (Leave -> clear); `inspectable=false ax_windows>0` is an exhausted walk (hold).
- Thresholds unchanged; info/debug log split verified by tests; public `run_and_call` interface preserved.
- Advisory: zero AX windows cannot distinguish Leave from all-windows-on-another-Space; the plan deliberately treats it as Leave.
