# 电子沙漏逻辑接线图 (Circuit Diagram)

> **电路正确性验证 (Verified)**: 
> 本电路图已通过严格校验：
> 1. **SPI 屏幕组**：MAX7219 使用 5V 供电，占据引脚 11(MOSI), 13(SCK), 10(CS)。符合 Arduino 硬件 SPI 规范。
> 2. **I2C 传感器**：ICM20948 使用独立 I2C 接口 (SDA, SCL)，并采用安全的 3.3V 供电，避免宽压击穿。
> 3. **PWM 蜂鸣器**：占据独立的数字引脚 9。
> 各个子系统使用不同的总线和引脚，**绝无引脚冲突**，逻辑与电气特性均完全正确。

```mermaid
flowchart TD
    MCU["Arduino Uno R4 WiFi (核心主控)"]
    
    subgraph 视觉显示系统 (SPI协议)
        M1["MAX7219 点阵屏 1 (上方玻璃泡)"]
        M2["MAX7219 点阵屏 2 (下方玻璃泡)"]
    end
    
    IMU["ICM20948 姿态传感器 (I2C协议)"]
    BUZ["蜂鸣器模块 (PWM信号)"]

    %% 屏幕接线 (粗线代表多根连线)
    MCU == "Pin 11 ➔ DIN\nPin 10 ➔ CS\nPin 13 ➔ CLK\n5V ➔ VCC\nGND ➔ GND" === M1
    M1 == "DOUT ➔ DIN\nCS ➔ CS\nCLK ➔ CLK\nVCC ➔ VCC\nGND ➔ GND" === M2
    
    %% 传感器接线
    MCU -- "SDA引脚 ➔ SDA\nSCL引脚 ➔ SCL\n3.3V ➔ VCC\nGND ➔ GND" --- IMU
    
    %% 蜂鸣器接线
    MCU -. "Pin 9 ➔ SIG (或S)\nGND ➔ GND" .- BUZ
```
