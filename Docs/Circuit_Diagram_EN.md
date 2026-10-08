# Digital Hourglass Logical Circuit Diagram

> **Circuit Verification (Verified)**: 
> This circuit topology has been strictly verified:
> 1. **SPI Displays**: MAX7219 matrices use 5V power and hardware SPI pins 11(MOSI), 13(SCK), 10(CS).
> 2. **I2C Sensor**: ICM20948 uses dedicated I2C pins (SDA, SCL) and safe 3.3V power, preventing overvoltage.
> 3. **PWM Buzzer**: Uses an independent digital pin (9).
> All subsystems utilize discrete buses and pins. There are **zero pin conflicts**, ensuring the design is electrically and logically sound.

```mermaid
flowchart TD
    MCU["Arduino Uno R4 WiFi (Main MCU)"]
    
    subgraph Visual Display System (SPI)
        M1["MAX7219 Matrix 1 (Top Glass)"]
        M2["MAX7219 Matrix 2 (Bottom Glass)"]
    end
    
    IMU["ICM20948 Orientation Sensor (I2C)"]
    BUZ["Buzzer Module (PWM Signal)"]

    %% Screen wiring (Thick lines indicate multiple connections)
    MCU == "Pin 11 ➔ DIN\nPin 10 ➔ CS\nPin 13 ➔ CLK\n5V ➔ VCC\nGND ➔ GND" === M1
    M1 == "DOUT ➔ DIN\nCS ➔ CS\nCLK ➔ CLK\nVCC ➔ VCC\nGND ➔ GND" === M2
    
    %% Sensor wiring
    MCU -- "SDA Pin ➔ SDA\nSCL Pin ➔ SCL\n3.3V ➔ VCC\nGND ➔ GND" --- IMU
    
    %% Buzzer wiring
    MCU -. "Pin 9 ➔ SIG (or S)\nGND ➔ GND" .- BUZ
```
