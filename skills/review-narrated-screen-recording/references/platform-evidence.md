# Platform Interaction Evidence

Determine the recording surface from multiple signals, not aspect ratio alone. Record `unknown` when the evidence is insufficient.

## Desktop

Look for:

- mouse pointer position and movement
- hover, tooltip, focus, pressed, selected, and context-menu states
- click indicators or pointer highlights added by the recorder
- keyboard focus, shortcuts, text selection, and window switching
- window chrome, browser tabs, title bars, scrollbars, and resizable panels

Use at least one frame before the action, the action frame, and one frame after it. A resting pointer does not prove a click. Confirm the target through a click indicator, pressed state, focus change, navigation, or another immediate result.

The narration may lead or lag the pointer. Align the request to the control being discussed across the nearby frame sequence, not only the frame at the transcript midpoint.

## Mobile

Look for:

- visible touch indicators when enabled
- immediate button, tab, sheet, modal, navigation, or loading-state changes
- scroll direction and content displacement for swipes
- long-press menus, pull-to-refresh, pinch/zoom, back gestures, and keyboard appearance
- status bar, safe area, home indicator, navigation bar, and on-screen keyboard

Screen recordings often do not show the finger or exact tap coordinate. When no touch indicator exists, identify the likely target from the before/after state transition and label the tap position as inferred. Do not claim that a specific button was tapped when multiple nearby controls could cause the same result.

For gestures, inspect enough frames to distinguish a swipe from a tap followed by navigation. Account for animation and network latency between the physical action and visible result.

## Tablet, Simulator, And Remote Sessions

Treat mixed evidence explicitly:

- A mobile simulator controlled by a desktop pointer is `mobile UI / mouse input`.
- A tablet with trackpad support may contain both hover and touch behavior.
- Remote desktop recordings may show pointer lag or duplicated cursors.
- Mirrored phone recordings may show desktop chrome around a mobile viewport.

Report the UI surface and input method separately instead of forcing one platform label.

## Required Evidence Fields

For each interaction-related checklist item, record:

- `surface`: desktop, mobile, tablet, simulator, remote, or unknown
- `input_method`: mouse, touch, keyboard, gesture, mixed, or inferred
- `indicator`: pointer, click highlight, touch dot, focus, state transition, or none
- `target`: visible control or uncertain target group
- `result`: immediate visible state change
- `certainty`: high, medium, or low

