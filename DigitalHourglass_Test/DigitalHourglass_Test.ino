#include <Wire.h>
#include <Adafruit_ICM20X.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_Sensor.h>
#include "LedControl.h"

// --- MAX7219 点阵屏引脚配置 ---
// 根据连线：DIN接引脚11，CS接引脚10，CLK接引脚13
const int DIN_PIN = 11;
const int CS_PIN = 10;
const int CLK_PIN = 13;
const int NUM_MATRICES = 2; // 我们有两个 8x8 屏幕串联

// 初始化 LED Control，参数: (DIN, CLK, CS, 模块数量)
LedControl lc = LedControl(DIN_PIN, CLK_PIN, CS_PIN, NUM_MATRICES);

// --- ICM20948 传感器配置 ---
Adafruit_ICM20948 icm;
Adafruit_Sensor *icm_accel;

void setup() {
  // 初始化串口通信，波特率 115200（用于在电脑上查看数据）
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  Serial.println("沙漏项目 - 基础硬件测试开始！");

  // --- 初始化 MAX7219 点阵屏 ---
  Serial.println("正在唤醒点阵屏...");
  for (int i = 0; i < NUM_MATRICES; i++) {
    lc.shutdown(i, false); // 唤醒屏幕 (默认是睡眠模式)
    lc.setIntensity(i, 8); // 设置亮度 (0~15，8属于中等亮度)
    lc.clearDisplay(i);    // 清空屏幕
  }
  
  // 开机动画：点亮每个屏幕的一个角落，确认屏幕编号 (0号和1号)
  lc.setLed(0, 0, 0, true); // 0号屏幕，第0行第0列亮
  lc.setLed(1, 7, 7, true); // 1号屏幕，第7行第7列亮
  delay(1000);
  for (int i = 0; i < NUM_MATRICES; i++) lc.clearDisplay(i);

  // --- 初始化 ICM20948 传感器 ---
  Serial.println("正在寻找 ICM20948 传感器...");
  // 尝试通过 I2C 接口连接传感器
  if (!icm.begin_I2C()) { 
    Serial.println("找不到 ICM20948！请检查 I2C 接线 (SDA/SCL)。");
    while (1) {
      delay(10); // 如果找不到，就在这里死循环停住
    }
  }
  Serial.println("成功连接 ICM20948 传感器！");
  
  // 获取加速度计数据接口
  icm_accel = icm.getAccelerometerSensor();
}

void loop() {
  // 1. 获取传感器最新数据
  sensors_event_t accel;
  icm_accel->getEvent(&accel);

  // 2. 将加速度数据打印到“串口监视器”
  Serial.print("加速度 X: "); Serial.print(accel.acceleration.x);
  Serial.print(" | Y: "); Serial.print(accel.acceleration.y);
  Serial.print(" | Z: "); Serial.print(accel.acceleration.z);
  Serial.println(" m/s^2");

  // 3. 简单的联动测试：倾斜板子点亮不同的屏幕
  // 注意：X/Y/Z轴的具体数值取决于你如何物理固定传感器。
  // 这里的逻辑是：如果 X 轴倾斜，就点亮对应的屏幕。
  
  if (accel.acceleration.x > 5.0) {
    // 往一侧倾斜，点亮 0号 屏幕，熄灭 1号
    fillMatrix(0, true);
    fillMatrix(1, false);
  } else if (accel.acceleration.x < -5.0) {
    // 往另一侧倾斜，点亮 1号 屏幕，熄灭 0号
    fillMatrix(0, false);
    fillMatrix(1, true);
  } else {
    // 平放时，全灭
    fillMatrix(0, false);
    fillMatrix(1, false);
  }

  // 稍作延时，避免数据刷新过快
  delay(200); 
}

// 自定义辅助函数：点亮或熄灭整个矩阵
void fillMatrix(int matrixIndex, bool state) {
  for (int row = 0; row < 8; row++) {
    for (int col = 0; col < 8; col++) {
      lc.setLed(matrixIndex, row, col, state);
    }
  }
}
