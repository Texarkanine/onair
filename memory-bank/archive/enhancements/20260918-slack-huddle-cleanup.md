---
task_id: slack-huddle-cleanup
complexity_level: 2
date: 2026-09-18
status: completed
---

# TASK ARCHIVE: slack-huddle-cleanup

## SUMMARY

The macOS Slack Huddle detector pair shipped thinner: ctypes Accessibility stays, AppleScript was rejected as a replacement, and two review fixes landed after reflect (window-first AX walk; `AXManualAccessibility` enable errors no longer look like “other Space”).

## REQUIREMENTS

- Remove unused inspector surface without changing huddle matching, Space-hold, hysteresis, or “do not activate Slack.”
- Decide whether AppleScript can replace the ctypes Accessibility walk without compiling Swift.
- Do not add tests; Slack was not installed on the build machine.
- ctypes remains the live import path.

## IMPLEMENTATION

AppleScript cannot set Electron `AXManualAccessibility`: System Events errors because the attribute is absent from `AXUIElementCopyAttributeNames`. Electron documents only `AXUIElementSetAttributeValue`. No sibling osascript files.

Cleanup in [`client/toggles/macos/lib/slack_huddle_ax.py`](client/toggles/macos/lib/slack_huddle_ax.py) and [`client/toggles/macos/slack_huddle.py`](client/toggles/macos/slack_huddle.py): dropped `named_windows`, unused toolbar matching, and the diagnostic `signals` list. Huddle is a window title starting with `Huddle:` or a Leave huddle button.

Post-reflect review:

- Scan `AXWindows` titles first; a DFS that blows the node budget is unreadable (hold), not `huddle=false`.
- Check the `AXManualAccessibility` `AXError`. `AttributeUnsupported` is ignored (Electron has returned that even when the set worked). Other errors with an empty window list fail the inspector as `ax_manual_failed:<code>`.

## TESTING

No test runner and no Slack. Verification was review, `python -m py_compile`, `/niko-qa` PASS, and two Cursor review rounds on PR #9. Live huddle detection was not run.

## LESSONS LEARNED

- Chromium `osascript` in this repo is a different API and does not generalize to Electron AX.
- The no-Swift inspector is in-process C calls to enable the tree, then a boolean walk, then the same poll/hysteresis loop as other macOS toggles. AppleScript would never have been the foundation.
- When a dict has both dead and live keys, write “replace” not “delete,” or the builder can drop the live half (`flags["leave"]` was live).

## PROCESS IMPROVEMENTS

Plan language for mixed live/dead fields should say replace-with-direct-tracking, not delete the dict.

## TECHNICAL IMPROVEMENTS

ctypes `argtypes` stay; they are the Accessibility C API, not leftover abstraction.

## NEXT STEPS

Run the toggle against a real Slack huddle (including another Space, and a `Huddle:` window behind a large main window). None otherwise.
