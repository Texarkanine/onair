# Tech Context

Python 3 suite in three independent Pipenv projects: `client/`, `server/`, and `sign/src/`. There is no monorepo build. Flask serves HTTP on the server and the sign; the client is a long-running watcher.

## Environment Setup

Each component has its own `Pipfile`. Client and server require Python 3.10; the sign requires Python 3.11. Install dependencies with pipenv from that component's directory.

The reference sign host is a Raspberry Pi Zero W (not the Zero 2 W). `sign/install/rpi-zerow/Makefile` installs pyenv/pipx/pipenv, udev rules, hidapitester, and an optional systemd unit. That unit template assumes a USB HID relay and a register URL.

A sample macOS LaunchAgent plist lives in `client/README.md`.

## Build Tools

No project-wide Makefile or packaging. Runtime is `pipenv run python` against:

- `client/watcher.py`
- `server/server.py`
- `sign/src/sign.py`

Pi bootstrap lives at `sign/install/rpi-zerow/Makefile`.

The shared API prefix is assembled as `/onair/api` + `v1` in `server/server.py` and `sign/src/sign.py`. Server and sign currently bind `0.0.0.0` and start Flask with `debug=True`.

## Testing Process

There is no test suite or test runner in this repository yet. When tests exist, follow `.cursor/rules/shared/always-tdd.mdc` and `.cursor/rules/shared/test-running-practices.mdc`.
