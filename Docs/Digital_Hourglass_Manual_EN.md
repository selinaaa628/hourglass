# Digital LED Hourglass: CDIO Project & Operation Manual

## 1. Project Overview
This manual details an advanced, interactive "Digital LED Hourglass". Beyond orientation-based gravity simulation and digital readouts, it features **customizable countdown durations via a membrane keypad**, elevating it from a novelty to a highly practical utility device.

## 2. Hardware Wiring Guide
The system is powered by an Arduino Uno R4 WiFi.

### NEW: 4x4 Membrane Keypad Wiring
Connect the 8-pin flat ribbon cable of the keypad from left to right:
*   **Row Pins (Left 4 wires)**: Connect to Arduino Digital Pins **2, 3, 4, 5**.
*   **Col Pins (Right 4 wires)**: Connect to Arduino Digital Pins **6, 7, 8, 12**.

*(For displays, sensor, and buzzer wiring, refer to the dedicated Circuit Diagram files).*

## 3. Inclusive & Interactive Design (Conceive & Design)
Introducing the keypad breaks the limitation of a hardcoded timer:
1.  **Immediate Feedback**: Keystrokes generate audio clicks and shift the digits leftwards on the rear display, mimicking familiar calculator interfaces.
2.  **Error Correction**: The `C` (Clear) button instantly resets the input buffer, providing a safety net for typos.
3.  **Explicit Confirmation**: The `#` key commits the timer to memory, preventing accidental mid-countdown alterations.

## 4. Software Algorithms & Logic (Implement)
The state machine has been expanded to parse matrix keypad inputs seamlessly without `delay()`:
*   **Dynamic Time Parsing**: Upon pressing `#`, the buffer (e.g., `['0','5','0','0']`) is mathematically parsed into milliseconds. The physics engine dynamically recalculates the `dropInterval` for the 64 sand particles.
*   **Foolproofing (Edge Cases)**: Inputs resolving to 0 milliseconds are caught and clamped to 1000ms. Keystrokes during the active falling state (`TIMING`) are safely ignored to ensure timer integrity.

## 5. Operation Guide (Operate)
1. **Boot**: Power on the device. The rear display defaults to `0500` (5 mins).
2. **Set Timer**: Use the keypad to punch in MMSS. For 2 minutes 30 seconds, type `0` `2` `3` `0`. Press `C` to clear if you make a mistake.
3. **Confirm**: Press `#`. A confirmation beep will sound.
4. **Start**: Flip the hourglass 180 degrees. The sand and countdown will commence based on your new, custom duration!
