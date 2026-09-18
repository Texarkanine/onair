# Read Slack huddle UI through the macOS Accessibility C API (ctypes).
# The process that starts this toggle must have Accessibility permission.
# Slack is Electron. The AX tree is empty until AXManualAccessibility is true.
# System Events AppleScript cannot set that attribute; this file calls the C API.
# Slack English UI labels. A localized Slack client does not match.
# This inspector does not activate Slack.

import ctypes
import ctypes.util
import subprocess
from ctypes import POINTER, c_int32, c_long, c_ubyte, c_uint32, c_void_p, c_char_p

_CF = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))
_AX = ctypes.cdll.LoadLibrary(ctypes.util.find_library("ApplicationServices"))

kCFStringEncodingUTF8 = 0x08000100
kAXErrorSuccess = 0

_CF.CFStringCreateWithCString.argtypes = [c_void_p, c_char_p, c_uint32]
_CF.CFStringCreateWithCString.restype = c_void_p
_CF.CFStringGetLength.argtypes = [c_void_p]
_CF.CFStringGetLength.restype = c_long
_CF.CFStringGetCString.argtypes = [c_void_p, c_char_p, c_long, c_uint32]
_CF.CFStringGetCString.restype = c_ubyte
_CF.CFArrayGetCount.argtypes = [c_void_p]
_CF.CFArrayGetCount.restype = c_long
_CF.CFArrayGetValueAtIndex.argtypes = [c_void_p, c_long]
_CF.CFArrayGetValueAtIndex.restype = c_void_p
_CF.CFGetTypeID.argtypes = [c_void_p]
_CF.CFGetTypeID.restype = ctypes.c_ulong
_CF.CFArrayGetTypeID.argtypes = []
_CF.CFArrayGetTypeID.restype = ctypes.c_ulong
_CF.CFStringGetTypeID.argtypes = []
_CF.CFStringGetTypeID.restype = ctypes.c_ulong
_CF.CFRelease.argtypes = [c_void_p]
_CF.CFRelease.restype = None

_AX.AXIsProcessTrusted.argtypes = []
_AX.AXIsProcessTrusted.restype = c_ubyte
_AX.AXUIElementCreateApplication.argtypes = [c_int32]
_AX.AXUIElementCreateApplication.restype = c_void_p
_AX.AXUIElementSetAttributeValue.argtypes = [c_void_p, c_void_p, c_void_p]
_AX.AXUIElementSetAttributeValue.restype = c_int32
_AX.AXUIElementCopyAttributeValue.argtypes = [c_void_p, c_void_p, POINTER(c_void_p)]
_AX.AXUIElementCopyAttributeValue.restype = c_int32

_kCFBooleanTrue = c_void_p.in_dll(_CF, "kCFBooleanTrue")


def _cfstr(text: str):
    return _CF.CFStringCreateWithCString(None, text.encode("utf-8"), kCFStringEncodingUTF8)


_AX_ROLE = _cfstr("AXRole")
_AX_TITLE = _cfstr("AXTitle")
_AX_DESC = _cfstr("AXDescription")
_AX_CHILDREN = _cfstr("AXChildren")
_AX_WINDOWS = _cfstr("AXWindows")
_AX_MANUAL = _cfstr("AXManualAccessibility")


def _cfstring_to_str(ref):
    if not ref:
        return None
    if _CF.CFGetTypeID(ref) != _CF.CFStringGetTypeID():
        return None
    length = _CF.CFStringGetLength(ref)
    if length < 0:
        return None
    buf_size = (int(length) + 1) * 4
    buf = ctypes.create_string_buffer(buf_size)
    if not _CF.CFStringGetCString(ref, buf, buf_size, kCFStringEncodingUTF8):
        return None
    return buf.value.decode("utf-8")


def _copy_attr(element, name_ref):
    value = c_void_p()
    err = _AX.AXUIElementCopyAttributeValue(element, name_ref, ctypes.byref(value))
    if err != kAXErrorSuccess or not value.value:
        return None
    return value


def _copy_str(element, name_ref):
    value = _copy_attr(element, name_ref)
    if value is None:
        return None
    try:
        return _cfstring_to_str(value)
    finally:
        _CF.CFRelease(value)


def _array_count(element, name_ref):
    value = _copy_attr(element, name_ref)
    if value is None:
        return 0
    try:
        if _CF.CFGetTypeID(value) != _CF.CFArrayGetTypeID():
            return 0
        return int(_CF.CFArrayGetCount(value))
    finally:
        _CF.CFRelease(value)


def _walk_children(element, name_ref, visitor):
    # Keep the CFArray alive while visitor runs. Child refs die when the array is released.
    value = _copy_attr(element, name_ref)
    if value is None:
        return
    try:
        if _CF.CFGetTypeID(value) != _CF.CFArrayGetTypeID():
            return
        count = _CF.CFArrayGetCount(value)
        for i in range(count):
            child = _CF.CFArrayGetValueAtIndex(value, i)
            if child:
                visitor(child)
    finally:
        _CF.CFRelease(value)


def _normalized(value):
    if not value:
        return ""
    return " ".join(value.split()).lower()


def _slack_pid():
    # Main Slack desktop process. Helpers have other names.
    try:
        out = subprocess.check_output(["pgrep", "-x", "Slack"], text=True)
    except subprocess.CalledProcessError:
        return None
    pids = [int(line) for line in out.splitlines() if line.strip()]
    return pids[0] if pids else None


def _huddle_in(element, depth, budget):
    if depth > 20 or budget[0] <= 0:
        return False
    budget[0] -= 1

    role = _copy_str(element, _AX_ROLE) or ""
    title = _copy_str(element, _AX_TITLE)
    description = _copy_str(element, _AX_DESC)

    if _normalized(title).startswith("huddle:"):
        return True
    if role == "AXButton" and (
        _normalized(title) == "leave huddle" or _normalized(description) == "leave huddle"
    ):
        return True

    found = False

    def visit(child):
        nonlocal found
        if not found:
            found = _huddle_in(child, depth + 1, budget)

    _walk_children(element, _AX_CHILDREN, visit)
    return found


def inspect_slack_huddle() -> dict:
    report = {
        "ok": True,
        "running": False,
        "ax_windows": 0,
        "inspectable": False,
        "huddle": False,
        "error": None,
    }

    if not _AX.AXIsProcessTrusted():
        report["ok"] = False
        report["error"] = "accessibility_untrusted"
        return report

    pid = _slack_pid()
    if pid is None:
        return report

    report["running"] = True
    app_ref = _AX.AXUIElementCreateApplication(pid)
    if not app_ref:
        report["ok"] = False
        report["error"] = "ax_app_missing"
        return report

    try:
        _AX.AXUIElementSetAttributeValue(app_ref, _AX_MANUAL, _kCFBooleanTrue)

        report["ax_windows"] = _array_count(app_ref, _AX_WINDOWS)
        report["inspectable"] = report["ax_windows"] > 0
        report["huddle"] = _huddle_in(app_ref, 0, [3000])
        return report
    finally:
        _CF.CFRelease(app_ref)
