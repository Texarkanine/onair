---
task_id: slack-huddle-cleanup
date: 2026-09-18
complexity_level: 2
---

# Reflection: slack-huddle-cleanup

## Summary

The Slack Huddle pair is thinner: unread report fields and toolbar matching are gone, the AX walk returns a huddle boolean and stops at the first hit. ctypes stays; AppleScript cannot set Electron `AXManualAccessibility`.

## Requirements vs Outcome

Cleanup and the AppleScript question both landed. No sibling inspector files: acceptance allowed a recorded rejection, and that is what shipped. Tests were not added, per the brief.

## Plan Accuracy

File list and keep-list were right. The only wording trap was "delete the flags dict," which would have sounded like dropping live Leave-huddle detection; preflight caught it. No surprises in build.

## Build & QA Observations

Build was one rewrite of the walk plus a log-line trim. QA passed with no rework. Nothing here was executed against Slack.

## Insights

### Technical
- System Events AppleScript cannot set `AXManualAccessibility` because the attribute is missing from `AXUIElementCopyAttributeNames`. The no-Swift path is ctypes (or ObjC/Swift) calling `AXUIElementSetAttributeValue`. Chromium `osascript` in this repo is a different API and does not generalize.

### Process
- When a dict has both dead and live keys, write "replace" not "delete," or the builder can drop the live half.

### Million-Dollar Question

This is the shape you'd want from the start: in-process Accessibility C calls to flip Electron's AX tree on, then a boolean walk, then the same poll/hysteresis loop as the other macOS toggles. AppleScript would never have been the foundation.
