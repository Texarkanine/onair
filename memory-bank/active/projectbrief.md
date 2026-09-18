# Project Brief

## User Story

As a maintainer of the macOS Slack Huddle toggle, I want the detector pair cleaned of unused and overbuilt code, and I want AppleScript checked as a possible replacement for the ctypes Accessibility walk, so the implementation stays simple without compiling Swift.

## Use-Case(s)

### Use-Case 1

A reader of `client/toggles/macos/slack_huddle.py` and `client/toggles/macos/lib/slack_huddle_ax.py` can follow the huddle-detection logic without dead fields, unused flags, or extra machinery that is not doing work.

### Use-Case 2

AppleScript is tried as an inspector in new files next to the working pair. The ctypes inspector stays until something else is proven.

## Requirements

1. Clean up `client/toggles/macos/slack_huddle.py` and `client/toggles/macos/lib/slack_huddle_ax.py` by removing unused and over-engineered code.
2. Preserve existing detector behavior: poll Slack through Accessibility, debounce start/stop, hold last confirmed state when Slack is running but not inspectable (other Space), do not activate Slack.
3. Investigate whether AppleScript can inspect Slack instead of ctypes talking to the Accessibility C API.
4. Put any AppleScript experiment in new files beside the working pair; do not replace the ctypes inspector as part of the experiment.

## Constraints

1. Slack is not installed on this machine; live huddle inspection cannot be run here.
2. This repository has no test suite for this toggle; do not add tests as part of this work.
3. The ctypes path exists to avoid compiling Swift. AppleScript is only interesting if it covers the same job without Swift and without a worse maintenance shape.
4. English Slack UI labels are the match surface today; that limitation stays unless cleanup forces a change.

## Acceptance Criteria

1. The working pair is smaller or simpler, with no leftover report fields or flags that nothing reads.
2. AppleScript is either shown in side-by-side files as a candidate, or rejected in the task record with a concrete reason it cannot replace ctypes here.
3. The ctypes inspector remains the live import path unless a later decision (after this task) switches it.
