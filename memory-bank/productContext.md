# Product Context

## Target Audience

People who build their own physical "On Air" indicator — typically a small computer inside a sign — and want it to light when they are in a meeting, on a video call, recording, or otherwise unavailable. This is a DIY kit, not a packaged product. The intended sign computer is a Raspberry Pi Zero W (not the Zero 2 W); other hosts can run the same software.

## Use Cases

- Light a sign outside a room so others know not to interrupt
- Light a second sign inside the room so the person who is busy can see the same state
- Keep several signs in sync when more than one workstation can go on-air
- Run a single workstation talking straight to a single sign, with no middle service
- Unplug or reboot a sign and have it pick up the current state when it comes back — only when a central service is in the middle

## Key Benefits

- One shared on/off meaning across every sign
- Signs can appear and disappear without reconfiguring workstations
- The workstation never has to accept inbound connections
- The lamp or relay is whatever command the sign can run; the software does not assume a particular fixture

## Success Criteria

- When someone goes on-air, every connected sign shows on-air
- When they go off-air, every connected sign shows off-air
- A sign that was offline comes online already showing the current state, if a central service is in use
- A failed or unreachable sign does not stop the others

## Key Constraints

- Licensed AGPL-3.0; this is source you assemble and run yourself
- Without a central service, a sign that restarts stays off until the workstation next changes state
- Workstation software only pushes; it does not listen
- The reference sign is a Pi Zero W with a USB HID relay; other hardware is supported only by swapping the command the sign runs
- Documentation is intentionally thin; you are expected to DIY
