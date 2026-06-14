
/*
 * 项目名称：红树林生态监测终端 (ESP32) 
 * 当前版本：无土壤版 + PH电压调试 + 5秒高频心跳
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>

// 传感器核心库 (请确保在"管理库"中已安装)
#include <OneWire.h>
#include <DallasTemperature.h>
#include "DHT.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <BH1750.h>

// ================= 配置区 (烧录前必改) =================
const char* STASSID = "1206";    // 替换为你的WiFi名
const char* STAPSK  = "123456788";    // 替换为你的WiFi密码
const char* SERVER_IP = "10.77.133.114"; // 替换为你电脑真实的 IPv4 地址
const int SERVER_PORT = 5000;            // 后端端口(勿动)
// =======================================================

// 引脚定义
#define PIN_DS18B20 4
#define PIN_DHT     5
#define PIN_PH      34

// 对象初始化
OneWire oneWire(PIN_DS18B20);
DallasTemperature sensors(&oneWire);
DHT dht(PIN_DHT, DHT11);
Adafruit_BMP280 bmp; 
BH1750 lightMeter;

// 全局变量
float val_w_temp = 0.0;
float val_ph_voltage = 0.0; // 重点：存储PH电压用于调试
float val_ph     = 0.0;
float val_a_temp = 0.0;
float val_hum    = 0.0;
float val_lux    = 0.0;
float val_press  = 0.0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- 红树林监测系统节点端启动 ---");

  // 初始化传感器
  sensors.begin();
  dht.begin();
  Wire.begin(); 
  lightMeter.begin();

  if (!bmp.begin(0x76)) {
    Serial.println("警告: 未找到BMP280气压计，请检查I2C接线");
  }

  // 连接 WiFi
  WiFi.begin(STASSID, STAPSK);
  Serial.print("连接WiFi中");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi连接成功！当前设备IP: " + WiFi.localIP().toString());
}

void loop() {
  // 1. 读取传感器数据
  readSensors();

  // 2. 串口打印调试信息 (重点看PH电压)
  printDebugInfo();

  // 3. 上传数据到后端
  if (WiFi.status() == WL_CONNECTED) {
    sendDataToServer();
  }

  // 5秒发送一次，配合大屏的实时跳动与心跳离线检测
  delay(5000); 
}

void readSensors() {
  // --- 水温 ---
  sensors.requestTemperatures(); 
  val_w_temp = sensors.getTempCByIndex(0);
  if (val_w_temp == -127.00) val_w_temp = 0.0; 

  // --- PH传感器 (核心调试逻辑) ---
  int ph_adc = analogRead(PIN_PH); 
  val_ph_voltage = ph_adc * (3.3 / 4095.0); // ESP32基准电压为3.3V
  
  // 校准公式: 把模块上的蓝色螺丝拧到输出 2.5V 左右，此时PH显示为 7.0
  val_ph = 7.0 + ((2.5 - val_ph_voltage) * 3.0); 
  if(val_ph < 0) val_ph = 0;
  if(val_ph > 14) val_ph = 14;

  // --- 空气温湿度 ---
  val_hum = dht.readHumidity();
  val_a_temp = dht.readTemperature();

  // --- 光照 & 气压 ---
  val_lux = lightMeter.readLightLevel();
  val_press = bmp.readPressure() / 100.0F; 
}

void sendDataToServer() {
  HTTPClient http;
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/upload";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // 构建JSON数据包
  StaticJsonDocument<300> doc;
  doc["station_id"] = 1;
  doc["w_temp"] = val_w_temp;
  doc["ph"] = val_ph;
  doc["a_temp"] = val_a_temp;
  doc["hum"] = val_hum;
  doc["lux"] = val_lux;
  doc["press"] = val_press;

  String body;
  serializeJson(doc, body);
  int code = http.POST(body);
  
  if (code == 200) {
    Serial.println("数据上传成功 (Code: 200)");
  } else if (code < 0) {
    Serial.println("无法连接到电脑，请检查SERVER_IP和Python后端是否启动！");
  } else {
    Serial.println("上传报错，服务器响应码: " + String(code));
  }
  
  http.end();
}

void printDebugInfo() {
  Serial.println("=========================");
  Serial.print("[环境] PH: "); Serial.println(val_ph);
  Serial.print("[环境] 水温: "); Serial.print(val_w_temp); Serial.println(" C");
  Serial.print("[环境] 气温: "); Serial.print(val_a_temp); Serial.print(" C | 湿度: "); Serial.print(val_hum); Serial.println(" %");
  Serial.print("[环境] 光照: "); Serial.print(val_lux); Serial.print(" lx | 气压: "); Serial.print(val_press); Serial.println(" hPa");
  Serial.println("=========================\n");
}