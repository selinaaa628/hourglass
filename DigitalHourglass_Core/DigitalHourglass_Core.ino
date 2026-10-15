#include <Wire.h>
#include <Adafruit_ICM20X.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_Sensor.h>
#include "LedControl.h"
#include <Keypad.h>

// --- 引脚定义 ---
const int DIN_PIN = 11;
const int CS_PIN = 10;
const int CLK_PIN = 13;
const int BUZZER_PIN = 9;

// --- 矩阵显示配置 ---
const int NUM_MATRICES = 6; 
LedControl lc = LedControl(DIN_PIN, CLK_PIN, CS_PIN, NUM_MATRICES);

// --- 传感器配置 ---
Adafruit_ICM20948 icm;
Adafruit_Sensor *icm_accel;

// --- 键盘配置 ---
const byte ROWS = 4; 
const byte COLS = 4; 
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
// 键盘从左到右 8 根排线，前 4 根是行，后 4 根是列
byte rowPins[ROWS] = {2, 3, 4, 5}; 
byte colPins[COLS] = {6, 7, 8, 12}; 
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// --- 时间与逻辑设置 ---
char inputBuffer[4] = {'0','5','0','0'}; // 默认 0500
unsigned long totalTimeMs = 5UL * 60UL * 1000UL; 
const int TOTAL_SAND = 64; 
unsigned long dropInterval = totalTimeMs / TOTAL_SAND; 

enum State { IDLE, SETTING, TIMING, DONE };
State currentState = IDLE;

int topSandCount = TOTAL_SAND; 
int bottomSandCount = 0;       
unsigned long lastDropTime = 0;
unsigned long timerStartTime = 0;

int currentTopMatrix = 0;      
int currentBottomMatrix = 1;

unsigned long lastBeepTime = 0;
bool buzzerActive = false;

// 字体字库
const byte fontDigits[10][8] = {
  {0x3C, 0x66, 0x66, 0x6E, 0x76, 0x66, 0x3C, 0x00}, // 0
  {0x18, 0x18, 0x38, 0x18, 0x18, 0x18, 0x7E, 0x00}, // 1
  {0x3C, 0x66, 0x06, 0x0C, 0x18, 0x30, 0x7E, 0x00}, // 2
  {0x3C, 0x66, 0x06, 0x1C, 0x06, 0x66, 0x3C, 0x00}, // 3
  {0x0C, 0x1C, 0x2C, 0x4C, 0x7E, 0x0C, 0x0C, 0x00}, // 4
  {0x7E, 0x60, 0x7C, 0x06, 0x06, 0x66, 0x3C, 0x00}, // 5
  {0x3C, 0x66, 0x60, 0x7C, 0x66, 0x66, 0x3C, 0x00}, // 6
  {0x7E, 0x06, 0x0C, 0x18, 0x18, 0x18, 0x18, 0x00}, // 7
  {0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0x00}, // 8
  {0x3C, 0x66, 0x66, 0x3E, 0x06, 0x66, 0x3C, 0x00}  // 9
};

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  
  for (int i = 0; i < NUM_MATRICES; i++) {
    lc.shutdown(i, false);
    lc.setIntensity(i, 8); 
    lc.clearDisplay(i);
  }

  if (!icm.begin_I2C()) {
    Serial.println("找不到 ICM20948 传感器!");
    while(1) delay(10);
  }
  icm_accel = icm.getAccelerometerSensor();

  tone(BUZZER_PIN, 1000, 200);
}

void loop() {
  unsigned long currentMillis = millis();
  
  // --- 键盘输入处理 ---
  char key = keypad.getKey();
  if (key) {
    if (currentState != TIMING) { // 只有在非倒计时期间才能设置
      if (key >= '0' && key <= '9') {
        currentState = SETTING;
        noTone(BUZZER_PIN);
        // 数字左移逻辑
        inputBuffer[0] = inputBuffer[1];
        inputBuffer[1] = inputBuffer[2];
        inputBuffer[2] = inputBuffer[3];
        inputBuffer[3] = key;
        tone(BUZZER_PIN, 2000, 50); // 按键音
      } else if (key == 'C') {
        currentState = SETTING;
        noTone(BUZZER_PIN);
        for(int i=0; i<4; i++) inputBuffer[i] = '0';
        tone(BUZZER_PIN, 1000, 100); // 清零提示音
      } else if (key == '#') {
        // 解析 MMSS 为毫秒
        int mm = (inputBuffer[0]-'0')*10 + (inputBuffer[1]-'0');
        int ss = (inputBuffer[2]-'0')*10 + (inputBuffer[3]-'0');
        totalTimeMs = (mm * 60UL + ss) * 1000UL;
        if (totalTimeMs == 0) totalTimeMs = 1000; // 防止设置为 0 卡死
        dropInterval = totalTimeMs / TOTAL_SAND;
        currentState = IDLE; 
        tone(BUZZER_PIN, 1500, 200); // 确认提示音
      }
    }
  }

  // --- 读取姿态传感器 ---
  sensors_event_t accel;
  icm_accel->getEvent(&accel);
  int newTopMatrix = currentTopMatrix;
  if (accel.acceleration.z > 5.0) {
    newTopMatrix = 0; 
  } else if (accel.acceleration.z < -5.0) {
    newTopMatrix = 1; 
  }
  
  // --- 翻转判定 ---
  if (newTopMatrix != currentTopMatrix) {
    currentTopMatrix = newTopMatrix;
    currentBottomMatrix = (currentTopMatrix == 0) ? 1 : 0;
    
    topSandCount = TOTAL_SAND;
    bottomSandCount = 0;
    currentState = TIMING;
    lastDropTime = currentMillis;
    timerStartTime = currentMillis;
    
    noTone(BUZZER_PIN);
    tone(BUZZER_PIN, 1200, 150);
    delay(200);
    tone(BUZZER_PIN, 1200, 150);
  }

  // --- 核心倒计时物理逻辑 ---
  long remainingSec = 0;
  if (currentState == TIMING) {
    long elapsed = currentMillis - timerStartTime;
    if (elapsed >= totalTimeMs) {
      elapsed = totalTimeMs;
      currentState = DONE;
      topSandCount = 0;
      bottomSandCount = TOTAL_SAND;
    }
    remainingSec = (totalTimeMs - elapsed) / 1000;

    if (currentMillis - lastDropTime >= dropInterval) {
      lastDropTime = currentMillis; 
      if (topSandCount > 0) {
        topSandCount--;
        bottomSandCount++;
      }
    }
  } else if (currentState == DONE) {
    if (currentMillis - lastBeepTime >= 500) { 
      lastBeepTime = currentMillis;
      if (buzzerActive) {
        noTone(BUZZER_PIN);
      } else {
        tone(BUZZER_PIN, 800); 
      }
      buzzerActive = !buzzerActive;
    }
  }

  // --- 渲染屏幕 ---
  lc.clearDisplay(0);
  lc.clearDisplay(1);
  fillMatrixLinear(currentTopMatrix, topSandCount);
  fillMatrixLinear(currentBottomMatrix, bottomSandCount);

  if (currentState == TIMING) {
    int m = remainingSec / 60;
    int s = remainingSec % 60;
    drawDigit(2, m / 10);
    drawDigit(3, m % 10);
    drawDigit(4, s / 10);
    drawDigit(5, s % 10);
  } else if (currentState == SETTING || currentState == IDLE) {
    // 待机或设置时，显示当前输入的倒计时配置
    drawDigit(2, inputBuffer[0] - '0');
    drawDigit(3, inputBuffer[1] - '0');
    drawDigit(4, inputBuffer[2] - '0');
    drawDigit(5, inputBuffer[3] - '0');
  } else if (currentState == DONE) {
    drawDigit(2, 0);
    drawDigit(3, 0);
    drawDigit(4, 0);
    drawDigit(5, 0);
  }
}

void drawDigit(int matrixIndex, int digit) {
  for (int row = 0; row < 8; row++) {
    lc.setRow(matrixIndex, row, fontDigits[digit][row]);
  }
}

void fillMatrixLinear(int matrixIndex, int count) {
  int ledsLit = 0;
  for (int row = 0; row < 8; row++) {
    for (int col = 0; col < 8; col++) {
      if (ledsLit < count) {
        lc.setLed(matrixIndex, row, col, true);
        ledsLit++;
      } else {
        return; 
      }
    }
  }
}
