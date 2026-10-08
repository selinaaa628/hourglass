#include <Wire.h>
#include <Adafruit_ICM20X.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_Sensor.h>
#include "LedControl.h"

// --- 引脚定义 ---
const int DIN_PIN = 11;
const int CS_PIN = 10;
const int CLK_PIN = 13;
const int BUZZER_PIN = 9; // 新增：蜂鸣器连接到数字引脚 9

const int NUM_MATRICES = 2;
LedControl lc = LedControl(DIN_PIN, CLK_PIN, CS_PIN, NUM_MATRICES);

Adafruit_ICM20948 icm;
Adafruit_Sensor *icm_accel;

// --- 时间与逻辑设置 ---
const unsigned long TOTAL_TIME_MS = 5UL * 60UL * 1000UL; // 5分钟转换为毫秒 (300,000 ms)
const int TOTAL_SAND = 64; // 一块屏幕的沙粒总数 (8x8 = 64)
const unsigned long DROP_INTERVAL = TOTAL_TIME_MS / TOTAL_SAND; // 计算每颗沙粒掉落的时间间隔 (约 4687 ms)

// 状态机定义
enum State {
  IDLE,    // 待机状态
  TIMING,  // 计时中状态
  DONE     // 计时完成状态
};
State currentState = IDLE;

// 核心变量
int topSandCount = TOTAL_SAND; // 上方沙粒剩余量
int bottomSandCount = 0;       // 下方沙粒堆积量
unsigned long lastDropTime = 0;

int currentTopMatrix = 0;      // 记录当前物理位置在"上方"的是哪个屏幕 (0或1)
int currentBottomMatrix = 1;

// 蜂鸣器非阻塞控制变量
unsigned long lastBeepTime = 0;
bool buzzerActive = false;

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // 初始化屏幕
  for (int i = 0; i < NUM_MATRICES; i++) {
    lc.shutdown(i, false);
    lc.setIntensity(i, 8); // 亮度 0-15
    lc.clearDisplay(i);
  }

  // 初始化传感器
  if (!icm.begin_I2C()) {
    Serial.println("找不到 ICM20948 传感器!");
    while(1) delay(10);
  }
  icm_accel = icm.getAccelerometerSensor();

  Serial.println("沙漏初始化完成。请垂直放置沙漏以启动！");
  
  // 开机提示音：短促滴一声
  tone(BUZZER_PIN, 1000, 200);
}

void loop() {
  unsigned long currentMillis = millis();
  
  // 1. 读取传感器数据，判断沙漏姿态
  sensors_event_t accel;
  icm_accel->getEvent(&accel);
  
  int newTopMatrix = currentTopMatrix;
  
  // 这里假设 Z 轴探测重力 (这取决于你如何把传感器固定在沙漏上)
  // 如果固定后发现翻转不灵敏，请尝试将 .z 改为 .x 或 .y
  if (accel.acceleration.z > 5.0) {
    newTopMatrix = 0; // 屏幕 0 在上
  } else if (accel.acceleration.z < -5.0) {
    newTopMatrix = 1; // 屏幕 1 在上
  }
  
  // 2. 检测到有效翻转动作！
  if (newTopMatrix != currentTopMatrix) {
    currentTopMatrix = newTopMatrix;
    currentBottomMatrix = (currentTopMatrix == 0) ? 1 : 0;
    
    // 重置沙粒和计时状态
    topSandCount = TOTAL_SAND;
    bottomSandCount = 0;
    currentState = TIMING;
    lastDropTime = currentMillis;
    noTone(BUZZER_PIN); // 确保翻转时停止之前的报警音
    
    Serial.println("检测到翻转！5分钟倒计时开始。");
    
    // 【无障碍功能】正确翻转时，鸣叫两声提醒盲人用户
    tone(BUZZER_PIN, 1200, 150);
    delay(200); // 这里的微小阻塞是为了保证提示音节奏，不影响大局
    tone(BUZZER_PIN, 1200, 150);
    delay(500); // 延时防抖，避免手抖导致连续触发
  }

  // 3. 核心倒计时逻辑
  if (currentState == TIMING) {
    // 检查是否到了该掉落一颗沙粒的时间
    if (currentMillis - lastDropTime >= DROP_INTERVAL) {
      lastDropTime = currentMillis; 
      
      if (topSandCount > 0) {
        topSandCount--;
        bottomSandCount++;
      }
      
      // 如果上方沙粒漏完，进入完成状态
      if (topSandCount == 0) {
        currentState = DONE;
        Serial.println("时间到！");
      }
    }
  } 
  // 4. 计时结束报警逻辑
  else if (currentState == DONE) {
    // 【无障碍功能】时间到后，蜂鸣器非阻塞式连续鸣叫 (每0.5秒响一次)
    if (currentMillis - lastBeepTime >= 500) { 
      lastBeepTime = currentMillis;
      if (buzzerActive) {
        noTone(BUZZER_PIN);
      } else {
        tone(BUZZER_PIN, 800); // 发出 800Hz 的声音
      }
      buzzerActive = !buzzerActive;
    }
  }

  // 5. 将沙粒渲染到屏幕上
  renderMatrices();
}

// 自定义函数：将内存中的沙粒数量显示到屏幕上
void renderMatrices() {
  lc.clearDisplay(0);
  lc.clearDisplay(1);

  // 简单渲染模式：根据沙粒数量点亮对应数量的 LED
  fillMatrixLinear(currentTopMatrix, topSandCount);
  fillMatrixLinear(currentBottomMatrix, bottomSandCount);
}

// 辅助函数：在一个 8x8 屏幕上点亮前 N 个 LED
void fillMatrixLinear(int matrixIndex, int count) {
  int ledsLit = 0;
  for (int row = 0; row < 8; row++) {
    for (int col = 0; col < 8; col++) {
      if (ledsLit < count) {
        lc.setLed(matrixIndex, row, col, true);
        ledsLit++;
      } else {
        return; // 点亮完毕，退出循环
      }
    }
  }
}
