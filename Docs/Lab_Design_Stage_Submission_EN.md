# ELEC281 Mini Challenge: Design Stage & Circuit Documentation
**Project:** Digital LED Hourglass with Accessibility & Dual-Sided Interface  
**Team / Box:** Box 34 | **Academic Year:** 2026–27  
**Module:** ELEC281 - Applied Electronic Skills and Engineering Practice  

---

## 1. High-Level Hardware Flow Diagram (Architecture)

The hardware architecture separates concerns into **Power Supply**, **Input/Sensing**, **Processing (MCU)**, and **Dual Output (Visual + Auditory)** subsystems.

```mermaid
flowchart TD
    %% Power Source
    PWR["USB 5V Power Supply\n(PC / Powerbank)"] -->|"VUSB (5V)"| MCU["Arduino Uno R4 WiFi\n(R7FA4M1 Core / 48MHz)"]
    
    %% Power Distribution
    MCU -->|"5V Rail & GND"| DISP_PWR["5V Power Bus"]
    MCU -->|"3.3V Low-Dropout Rail"| SENS_PWR["3.3V Clean Power"]

    %% Input Subsystem
    subgraph Inputs ["Input & Sensing Subsystem"]
        KP["4x4 Membrane Keypad\n(Time Configuration)"]
        IMU["ICM20948 / GY-87\n9DOF/10DOF Motion Sensor\n(Gravity / Flip Vector)"]
    end

    %% Bus Connections to MCU
    KP -->|"8x GPIOs (Pins 2-8, 12)\nRow/Col Matrix Scanning"| MCU
    IMU -->|"I2C Bus (SDA / SCL @ 400kHz)"| MCU
    SENS_PWR --> IMU

    %% Output Subsystem
    subgraph Outputs ["Feedback & Display Subsystem"]
        subgraph VisualFront ["Front Display (Sand Physics)"]
            M1["MAX7219 8x8 Matrix #0\n(Top Sand Chamber)"]
            M2["MAX7219 8x8 Matrix #1\n(Bottom Sand Chamber)"]
        end
        subgraph VisualBack ["Rear Display (Numeric MM:SS)"]
            M3["MAX7219 4-in-1 Matrix #2..5\n(Digital Countdown: MM:SS)"]
        end
        BUZ["Passive Buzzer\n(Accessibility Cues)"]
    end

    %% SPI Chain
    MCU -->|"SPI Bus (DIN=11, CS=10, CLK=13)"| M1
    M1 -->|"SPI Cascaded (DOUT->DIN)"| M2
    M2 -->|"SPI Cascaded (DOUT->DIN)"| M3
    DISP_PWR --> M1
    DISP_PWR --> M2
    DISP_PWR --> M3

    %% Buzzer PWM
    MCU -->|"PWM Signal (Pin 9, tone())"| BUZ
    MCU -->|"GND"| BUZ
```

### Hardware Flow Description
1. **Power Domain Separation**: The MAX7219 LED matrices (high dynamic current) are fed from the Arduino 5V rail. The sensitive inertial measurement unit (IMU) is powered from the regulated 3.3V rail to prevent electrical noise and over-voltage damage.
2. **High-Speed SPI Daisy Chaining**: All 6 display units (2 independent chambers + 4 digits) share a single 3-wire SPI interface (`DIN`, `CS`, `CLK`), significantly conserving microcontroller I/O pins.
3. **Dedicated I2C & Matrix GPIOs**: The motion sensor communicates over the standardized I2C bus (`SDA`, `SCL`), while the keypad occupies 8 general-purpose digital pins for fast row-column strobe scanning.

---

## 2. High-Level Software Flow Diagram (Firmware Architecture)

The software is implemented as an event-driven **Finite State Machine (FSM)** with non-blocking timing (`millis()` scheduler), guaranteeing real-time responsiveness to flips and keypad presses.

```mermaid
flowchart TD
    START(["Power-on / System Reset"]) --> INIT["BOOT_INIT\n- Initialize SPI, I2C, GPIOs, Keypad\n- Clear 6x MAX7219 Displays\n- Startup Chime tone(1000Hz, 200ms)"]
    INIT --> IDLE["IDLE_READY\n- Default timer set to 05:00\n- Rear display shows '05:00'\n- Await Keypad input OR Physical Flip"]

    %% Keypad branch
    IDLE -- "Key Pressed (0-9 or C)" --> SETTING["SETTING_MODE\n- Shift buffer left & append key\n- Audio click tone(2000Hz, 50ms)\n- Update rear preview (MMSS)\n- 'C' clears buffer to '0000'"]
    SETTING -- "Press '#' (Confirm)" --> COMMIT["Recalculate Duration\n- totalTimeMs = MM*60s + SS\n- dropInterval = totalTimeMs / 64\n- Confirmation beep tone(1500Hz)"]
    COMMIT --> IDLE

    %% Start Timing branch
    IDLE -- "Flip 180 deg (IMU Accel Z Inversion)" --> START_TIMING["TIMING_ACTIVE (Start)\n- Double-beep tone(1200Hz)\n- Reset sand (Top=64, Bottom=0)\n- Start timerStartTime = millis()"]
    SETTING -- "Flip 180 deg" --> START_TIMING

    %% Active timing loop
    START_TIMING --> LOOP{"Non-blocking Main Loop (millis)"}
    
    LOOP -- "millis() - lastDrop >= dropInterval" --> DROP["Drop Sand Grain\n- topSandCount--\n- bottomSandCount++\n- Refresh front LED matrices"]
    DROP --> LOOP

    LOOP -- "Every second" --> UPDATE_TIME["Update Rear Display\n- Calculate remaining MM:SS\n- Render digits on matrices 2-5"]
    UPDATE_TIME --> LOOP

    LOOP -- "180 deg Flip Detected mid-way" --> MID_FLIP["Mid-Flip Reversal\n- Swap Top and Bottom matrix IDs\n- Double-beep tone(1200Hz)\n- Restart countdown timer"]
    MID_FLIP --> LOOP

    %% Time Up branch
    LOOP -- "All sand dropped (topSand == 0)" --> DONE["ALARM_DONE (Time is Up!)\n- Rear display locks at '00:00'\n- Pulse alarm tone(800Hz) every 500ms\n- Await user acknowledgement"]
    
    DONE -- "Flip 180 deg (User Acknowledges)" --> START_TIMING
```

### Key Software Principles
* **Non-Blocking Architecture**: No `delay()` calls are used inside the active loops. Timer intervals, debounce windows, and buzzer chirps rely entirely on delta-time math (`millis() - previousMillis >= interval`).
* **Dynamic Physics Recalculation**: Changing countdown time dynamically scales the particle drop velocity:
  $$\text{dropInterval} = \frac{\text{totalTimeMs}}{64\text{ LEDs}}$$
* **Inclusive Accessibility Loop**: Audio confirmation accompanies every state change (key click, mode confirm, flip acknowledge, and continuous time-up alarm).

---

## 3. Implementation Circuit Diagram & Pin Specification

### 3.1 Master Interconnection Table

| Subsystem | Peripheral Module | Module Pin | Arduino Uno R4 WiFi Pin | Electrical Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **Power** | MAX7219 Displays (All) | VCC | **5V** | High current (up to 300mA peak) |
| | MAX7219 Displays (All) | GND | **GND** | System Common Ground |
| | IMU Sensor (ICM20948/GY-87)| VCC / 3V3 | **3.3V** | Regulated low-noise logic supply |
| | IMU Sensor | GND | **GND** | Common Ground |
| | Buzzer Module | GND | **GND** | Common Ground |
| **Visual SPI** | Matrix #0 (Top Sand) | DIN | **Pin 11 (COPI/MOSI)**| High-speed SPI Serial Data |
| | Matrix #0 (Top Sand) | CS / LOAD | **Pin 10 (SS)** | Active-Low Chip Select |
| | Matrix #0 (Top Sand) | CLK | **Pin 13 (SCK)** | SPI Serial Clock |
| **Daisy Chain**| Matrix #0 $\rightarrow$ Matrix #1 | DOUT $\rightarrow$ DIN | *Inter-module jumper* | Cascaded SPI data out |
| | Matrix #1 $\rightarrow$ Matrix #2..5 | DOUT $\rightarrow$ DIN | *Inter-module jumper* | Cascaded SPI data out |
| | All Matrices Shared | CS, CLK, VCC, GND | *Bus Jumper* | Parallel shared control lines |
| **I2C Motion** | IMU Sensor | SDA | **SDA** (or A4) | I2C Data (4.7kΩ internal pullup) |
| | IMU Sensor | SCL | **SCL** (or A5) | I2C Clock |
| **Audio** | Passive Buzzer | SIG / S | **Pin 9 (PWM)** | Square wave frequency synthesis |
| **4x4 Keypad** | Ribbon Pin 1 (Row 1) | R1 | **Pin 2** | Digital Input with Pullup |
| | Ribbon Pin 2 (Row 2) | R2 | **Pin 3** | Digital Input with Pullup |
| | Ribbon Pin 3 (Row 3) | R3 | **Pin 4** | Digital Input with Pullup |
| | Ribbon Pin 4 (Row 4) | R4 | **Pin 5** | Digital Input with Pullup |
| | Ribbon Pin 5 (Col 1) | C1 | **Pin 6** | Strobe Column Output |
| | Ribbon Pin 6 (Col 2) | C2 | **Pin 7** | Strobe Column Output |
| | Ribbon Pin 7 (Col 3) | C3 | **Pin 8** | Strobe Column Output |
| | Ribbon Pin 8 (Col 4) | C4 | **Pin 12** | Strobe Column Output |

### 3.2 Detailed Schematic Representation

```
                     +----------------------------------------------------+
                     |                ARDUINO UNO R4 WIFI                 |
                     |                                                    |
                     |   [5V]  [3.3V]  [GND]   [SDA]  [SCL]   [D9~]       |
                     +----+------+------+-------+------+-------+----------+
                          |      |      |       |      |       |
+-------------------------+      |      |       |      |       |
| (+5V Power Bus)                |      |       |      |       |
|                                |      |       |      |       |
|   +--------------------+       |      |       |      |       |
|   | ICM20948 / GY-87   |       |      |       |      |       |
|   | 9DOF Motion Sensor |       |      |       |      |       |
|   |                    |       |      |       |      |       |
|   | VCC <--------------+-------+      |       |      |       |
|   | GND <-----------------------------+       |      |       |
|   | SDA <-------------------------------------+      |       |
|   | SCL <--------------------------------------------+       |
|   +--------------------+                                     |
|                                                              |
|   +--------------------+                                     |
|   | Passive Buzzer     |                                     |
|   | SIG <----------------------------------------------------+
|   | GND <-----------------------------+
|   +--------------------+              |
|                                       |
|   +-----------------------------------+--------------------+
|   | 4x4 Membrane Keypad                                    |
|   | Rows (Pin 1..4)  =======> D2, D3, D4, D5 (Arduino)     |
|   | Cols (Pin 5..8)  =======> D6, D7, D8, D12 (Arduino)    |
|   +--------------------------------------------------------+
|
|   +-----------------------------------------------------------------------------+
|   | SPI DISPLAY DAISY CHAIN (6x MAX7219 8x8 Matrices)                           |
|   |                                                                             |
|   | Arduino: [D11/MOSI] ---------> DIN [Screen #0: Top Sand]                   |
|   |          [D10/CS]   ---+-----> CS                                           |
|   |          [D13/CLK]  ---+-----> CLK                                          |
|   |          [5V]       ---+-----> VCC                                          |
|   |          [GND]      ---+-----> GND                                          |
|   |                                  | DOUT                                     |
|   |                                  v                                          |
|   |                                 DIN [Screen #1: Bottom Sand]                |
|   |                             CS, CLK, VCC, GND shared                        |
|   |                                  | DOUT                                     |
|   |                                  v                                          |
|   |                                 DIN [Screen #2..5: 4-in-1 Rear MM:SS Timer] |
|   |                             CS, CLK, VCC, GND shared                        |
+---+-----------------------------------------------------------------------------+
```

---

## 4. Key Verification & Safety Checklist for Assessment
1. **No GPIO Bus Contention**:
   * SPI pins (10, 11, 13) are strictly dedicated to high-speed LED shifting.
   * I2C pins (SDA, SCL) are on separate hardware peripheral registers.
   * Keypad scanning uses general digital pins 2-8 and 12, leaving Pin 9 free for hardware timer PWM buzzer generation.
2. **Thermal & Short-Circuit Precaution**:
   * Inspect all DuPont female headers before powering on.
   * Never connect 5V to the IMU sensor 3.3V power pin.
   * Ensure power lines are connected with the USB unplugged.
