# Task: slack-huddle-cleanup

* Task ID: slack-huddle-cleanup
* Complexity: Level 2
* Type: simple enhancement (cleanup)

Strip unused and overbuilt code from the macOS Slack Huddle detector pair. Keep ctypes as the live inspector: AppleScript cannot set Electron's `AXManualAccessibility`, which this pair requires. Do not replace the working import path. Do not add tests.

## Test Plan (TDD)

### Behaviors to Verify

No new executable behavior. Cleanup must not change these existing behaviors (review-only; cannot be executed here):

- Accessibility untrusted → `ok=False`, `error=accessibility_untrusted`
- Slack process not running → `running=False`, no huddle, toggle counts toward stop
- Slack running with `ax_windows == 0` → `inspectable=False`, toggle holds last confirmed state and does not activate Slack
- Window title starts with `Huddle:` or a Leave huddle button is present → `huddle=True`; toggle calls `callback(True)` after `start_threshold` hits
- Readable and no huddle → toggle calls `callback(False)` after `stop_threshold` hits
- `callback` returning `None` → local `on_call` does not advance

### Test Infrastructure

- Framework: none. This repo has no test runner (`memory-bank/techContext.md`).
- Test location: none
- Conventions: none
- New test files: none
- Operator constraint: Slack is not installed; do not add tests. always-tdd Step 1.3 would stop and ask; the operator already answered. Verification is static review of the pair.

## Implementation Plan

### 1. Strip dead inspector surface — executable — done

- Files: `client/toggles/macos/lib/slack_huddle_ax.py`
- No tests: operator constraint (no runner, no Slack). TDD substages 1–3 skipped.

1. Stub tests: skipped
2. Stub interface: skipped (no new public function)
3. Write tests and run red: skipped
4. Write code and run green: in `inspect_slack_huddle` and helpers:
    - Delete `named_windows` (never written)
    - Delete toolbar matching, `_HUDDLE_TOOLBARS`, and the `flags` dict (`toolbar` is collected and unused; huddle is title-or-leave only)
    - Stop collecting a uniqueness-checked `signals` list; return a thinner report (`ok`, `running`, `inspectable`, `huddle`, `ax_windows`, `error`)
    - Early-exit the AX walk once huddle is confirmed
    - Keep: `AXIsProcessTrusted`, `pgrep -x Slack`, `AXUIElementSetAttributeValue` for `AXManualAccessibility`, `AXWindows` count for inspectable, CF retain/release, do not activate Slack
    - One-line comment that System Events AppleScript cannot set `AXManualAccessibility`

### 2. Match the toggle to the thinner report — executable — done

- Files: `client/toggles/macos/slack_huddle.py`
- No tests: same operator constraint. TDD substages 1–3 skipped.

1. Stub tests: skipped
2. Stub interface: skipped
3. Write tests and run red: skipped
4. Write code and run green:
    - Keep hysteresis (`start_threshold` / `stop_threshold`), Space-hold when running but not inspectable, and `callback` `None` handling
    - Log the remaining report fields only
    - Do not reshape the poll loop to a new pattern; sibling toggles already look like this

### 3. AppleScript verdict — prose/policy — done

- Files: `memory-bank/active/progress.md` (and the inspector comment in step 1)
- No tests: prose/policy artifact

1. Do not add sibling AppleScript/osascript files.
2. Record: System Events cannot set `AXManualAccessibility` (attribute is absent from `AXUIElementCopyAttributeNames`; Electron documents only the C/ObjC/Swift `AXUIElementSetAttributeValue` call). ctypes is the no-Swift path that actually works.
3. A hybrid (ctypes set + AppleScript walk) is more code, not less; skip it.

## Technology Validation

No new technology - validation not required.

AppleScript was considered as a ctypes replacement. It is already used in this repo (`macos_utils.get_chromium_browser_tab_urls` via `osascript`) for Chromium tab URLs, which is a different API. Evidence it cannot replace this inspector:

- Electron: [Manually enabling accessibility features](https://www.electronjs.org/docs/latest/tutorial/accessibility) shows only `AXUIElementSetAttributeValue` (ObjC/Swift).
- [electron#37465](https://github.com/electron/electron/issues/37465) / [electron#38102](https://github.com/electron/electron/issues/38102): `set value of attribute "AXManualAccessibility"` in System Events errors because the attribute is not listed, so the set is never attempted.

## Dependencies

- None new. Keep stdlib `ctypes` + `ApplicationServices` / `CoreFoundation`. Do not add PyObjC.

## Challenges & Mitigations

- Cannot run Slack or tests: only delete unused surface; do not change huddle matching, Space-hold, hysteresis, or `AXManualAccessibility`.
- AppleScript looks simpler until Electron's empty AX tree: reject it in this plan; do not leave a fake sibling inspector.
- Over-cleaning the poll loop: leave start/stop counters; they match how this toggle avoids flicker.

## Pre-Mortem

- Cleanup drops `AXManualAccessibility` or the unreadable-Space hold and huddle detection silently breaks: already covered by Challenge 1; those paths are marked keep.
- A side-by-side AppleScript file is committed and later swapped in because it looks cleaner: already covered by Challenge 2; step 3 forbids the files.
- Review-only verification ships a logic change disguised as cleanup: plan step 1 is deletion of unread fields/flags only; walk still keys off `Huddle:` title and Leave huddle.

## Status

- [x] Initialization complete
- [x] Test planning complete (TDD)
- [x] Implementation plan complete
- [x] Technology validation complete
- [x] Pre-Mortem complete
- [x] Preflight
- [x] Build
- [ ] QA
