# Progress

Fix the macOS Slack huddle toggle so Leave actually ends the call when Slack is still running with `huddle=false inspectable=false ax_windows=0`, and move the long inspector dump from info to debug.

**Complexity:** Level 1

## 2026-09-18 - COMPLEXITY-ANALYSIS - COMPLETE

* Work completed
    - Restated and confirmed intent (huddle is false after Leave, not true)
    - Classified as Level 1 (single-component bug fix)
* Decisions made
    - Level 1: skip plan, creative, preflight, reflect, and archive
* Insights
    - The stuck signature is the toggle's "unreadable / hold" branch, not a leftover `huddle=true`

## 2026-09-18 - BUILD - COMPLETE

* Work completed
    - Empty AXWindows after Leave is `clear` (counts toward off), not hold
    - Hold remains only when windows exist and the walk is unreadable
    - Info logs are short; inspector/hysteresis dump is debug
    - Added stdlib unittest coverage for observation kind, log split, and Leave callback
* Decisions made
    - Treat `ax_windows=0` as a decisive miss, matching the observed Leave signature
    - Use stdlib unittest next to the toggle; no new test runner dependency
* Insights
    - The previous other-Space hold used the same empty-window signature as Leave, so Leave could never end the call
