# Digital Hourglass Logical Circuit Diagram

> **Circuit Verification (Verified)**: 
> The latest version integrates a 4x4 matrix keypad. We utilized 8 spare digital pins (2-8, 12) for row/col scanning, completely avoiding the SPI (10-13) and I2C (A4, A5) buses. The system remains 100% free of pin conflicts.

```mermaid
flowchart TD
    MCU["Arduino Uno R4 WiFi (Main MCU)"]
    
    subgraph Visual_Display_System_SPI
        M1["Matrix 1 (Top Sand)"]
        M2["Matrix 2 (Bottom Sand)"]
        M3["4-in-1 Matrix (Rear Timer)"]
    end
    
    subgraph Control_and_Interaction
        KEYPAD["4x4 Membrane Keypad"]
        IMU["ICM20948 Orientation Sensor"]
        BUZ["Buzzer Module"]
    end

    %% Screen wiring 
    MCU == "Pin 11 ➔ DIN\nPin 10 ➔ CS\nPin 13 ➔ CLK\n5V ➔ VCC\nGND ➔ GND" === M1
    M1 == "DOUT ➔ DIN (Daisy Chain)" === M2
    M2 == "DOUT ➔ DIN (Daisy Chain)" === M3
    
    %% Keypad wiring
    MCU == "Pins 2,3,4,5 ➔ Left 4 wires (Rows)\nPins 6,7,8,12 ➔ Right 4 wires (Cols)" === KEYPAD

    %% Sensor & Buzzer wiring
    MCU == "SDA ➔ SDA\nSCL ➔ SCL\n3.3V ➔ VCC" === IMU
    MCU == "Pin 9 ➔ SIG\nGND ➔ GND" === BUZ
```
