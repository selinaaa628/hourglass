# Digital LED Hourglass: CDIO Project & Operation Manual

## 1. Project Overview
This manual outlines the technical implementation, step-by-step workflow, and operational guidelines for the "Digital LED Hourglass" project. Based on the CDIO (Conceive, Design, Implement, Operate) framework, this project aims to create an interactive, physical timer using microcontroller hardware.

## 2. Hardware Selection & Wiring Guide (Step-by-Step)
The system utilizes an Arduino Uno R4 WiFi, two MAX7219 8x8 LED Matrices for the "sand," an ICM20948 9DOF sensor for tilt detection, and a buzzer for auditory feedback.

Please ensure the power is **OFF** before wiring according to the following steps:

### Step 1: Connect the First LED Matrix (Top Screen)
Connect the Arduino to the **Input side (DIN)** of the first MAX7219 module:
| Arduino Uno R4 WiFi Pin | MAX7219 (Top) Input Pins | Function |
| :--- | :--- | :--- |
| `5V` | `VCC` | Power supply |
| `GND` | `GND` | Common ground |
| `Pin 11` | `DIN` | Data in (SPI MOSI) |
| `Pin 10` | `CS` (or LOAD) | Chip select |
| `Pin 13` | `CLK` | Clock |

### Step 2: Daisy-Chain the Second Matrix (Bottom Screen)
Connect the **Output side (DOUT)** of the first matrix to the **Input side (DIN)** of the second matrix using jumper wires:
| MAX7219 (Top) Output Pins | MAX7219 (Bottom) Input Pins | Function |
| :--- | :--- | :--- |
| `VCC` | `VCC` | Shared 5V power |
| `GND` | `GND` | Shared ground |
| `DOUT` | `DIN` | Pass data to the next screen |
| `CS` (or LOAD) | `CS` (or LOAD) | Shared chip select |
| `CLK` | `CLK` | Shared clock |

### Step 3: Connect the ICM20948 Orientation Sensor
This sensor uses I2C to transmit gravity data:
| Arduino Uno R4 WiFi Pin | ICM20948 Sensor | Function |
| :--- | :--- | :--- |
| `3.3V` (or 5V) | `VCC` (or 3V3 / +) | Power (3.3V recommended) |
| `GND` | `GND` (or -) | Ground |
| `SDA` (or A4) | `SDA` | I2C Data line |
| `SCL` (or A5) | `SCL` | I2C Clock line |

### Step 4: Connect the Buzzer (Accessibility Feature)
| Arduino Uno R4 WiFi Pin | Buzzer Module | Function |
| :--- | :--- | :--- |
| `Pin 9` | `SIG` (or S) | Signal input (PWM tone) |
| `GND` | `GND` (or -) | Ground |
| `5V` (If 3-pin module) | `VCC` (or +) | Power |

## 3. Inclusive Design & Accessibility (Conceive & Design)
A major highlight addressing CDIO stakeholder criteria is the **blind-friendly/visually-impaired accessible design**:
1.  **Tactile/Audio Confirmation:** When flipped to start the timer, the buzzer emits a sharp "double-beep." This provides immediate confirmation of a successful interaction for users who cannot see the screen.
2.  **Time-Up Alarm:** After the 5-minute timer completes, a continuous alarm loops until the user flips the device again. This ensures the timer remains highly functional as a real-world tool.

## 4. Software Algorithms & Core Logic (Implement)
The firmware uses a non-blocking state machine architecture:
*   **Precision Timer Math:** Target time is exactly 5 minutes (300,000 ms). With 64 "sand grains" per matrix, the interval drops one grain every **4,687 milliseconds**.
*   **Particle Simulation:** To ensure performance, we use "Particle Counting" instead of complex physics arrays. The code dynamically tracks `topSandCount` and `bottomSandCount`, rendering LEDs row-by-row from the bottom up to mimic piling sand.
*   **Tilt Interrupt:** The system polls the Z-axis gravity vector rapidly. Upon detecting a 180-degree flip, it logically swaps the top and bottom displays, resets the timer to zero, and plays the confirmation beep.
*   **Non-blocking Execution:** The `delay()` function is entirely replaced by `millis()` delta checks. This guarantees the device can immediately detect a flip even while the buzzer is sounding or the sand is waiting to drop.

## 5. Operation & Demonstration Guide (Operate)
### 5.1 Assembly Precautions
1.  **Screen Alignment:** The two screens must be perfectly vertically aligned on the physical chassis.
2.  **Rigid Sensor Mount:** The orientation sensor MUST be rigidly mounted (e.g., screwed or hot-glued) to the frame. Any loose movement relative to the screens will completely break the flip-detection logic.

### 5.2 User Demonstration Flow
1.  **Boot Up:** Connect USB power. You will hear a startup beep.
2.  **Start Timing:** Stand the hourglass vertically. Observers will see the sand drop exactly every 4.68 seconds.
3.  **Time is Up:** After 5 minutes, a continuous alarm will sound.
4.  **Interactive Reset:** Invite someone to flip the hourglass 180 degrees. The device will double-beep, silence the alarm, and seamlessly restart the 5-minute countdown.
