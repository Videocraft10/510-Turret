#include <ESP32Servo.h>

// --- RAW NATIVE GPIO PIN CONFIGURATION ---
#define PAN1_PIN 2    // Physical Pin IO2
#define PAN2_PIN 3    // Physical Pin IO3
#define TILT1_PIN 5   // Physical Pin IO5
#define TILT2_PIN 6   // Physical Pin IO6
#define LASER_PIN 4   // Physical Pin IO4

Servo pan1, pan2, tilt1, tilt2;
float panAngle = 90.0, tiltAngle = 90.0;

const int FRAME_W = 320, FRAME_H = 240;
const int DEADZONE = 8;
const float GAIN = 0.08;
const float SMOOTH = 0.35; 

float smoothCx = FRAME_W / 2.0, smoothCy = FRAME_H / 2.0;
unsigned long lastValid = 0;
const unsigned long LOST_TIMEOUT = 800; 

void setup() {
  // Your board handles the direct MacBook USB cable using standard Serial natively!
  Serial.begin(115200);
  Serial.setTimeout(5); 
  
  // Bind physical servo motors to designated GPIO channels
  pan1.attach(PAN1_PIN);
  pan2.attach(PAN2_PIN);
  tilt1.attach(TILT1_PIN);
  tilt2.attach(TILT2_PIN);
  
  // Designate tracking laser connection
  pinMode(LASER_PIN, OUTPUT);
  digitalWrite(LASER_PIN, LOW); // Safe startup default
  
  // Drive hardware gimbals immediately to standard 90-degree central idle targets
  pan1.write((int)panAngle);
  pan2.write((int)panAngle);
  tilt1.write((int)tiltAngle);
  tilt2.write((int)tiltAngle);
}

void loop() {
  // Read incoming packets from the default serial stream
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    int cx, cy, area;
    
    // Parse out incoming tracking payload string
    if (sscanf(line.c_str(), "%d,%d,%d", &cx, &cy, &area) == 3) {
      
      // Apply linear interpolation smoothing logic
      smoothCx = smoothCx + SMOOTH * (cx - smoothCx);
      smoothCy = smoothCy + SMOOTH * (cy - smoothCy);
      lastValid = millis(); // Reset safety timeout watchdog clock
      
      // Determine displacement boundaries relative to center crosshair
      int errX = smoothCx - FRAME_W / 2;
      int errY = smoothCy - FRAME_H / 2;
      
      // Update orientation trajectories only if outside defined structural deadzones
      if (abs(errX) > DEADZONE) panAngle -= errX * GAIN;
      if (abs(errY) > DEADZONE) tiltAngle += errY * GAIN;
      
      // Enforce physical travel limits to eliminate mechanical binding/stalling
      panAngle = constrain(panAngle, 0, 180);
      tiltAngle = constrain(tiltAngle, 30, 150);
      
      // Update hardware positions
      pan1.write((int)panAngle);
      pan2.write((int)panAngle);
      tilt1.write((int)tiltAngle);
      tilt2.write((int)tiltAngle);
      
      // Engage laser target indicator
      digitalWrite(LASER_PIN, HIGH);
    }
  }
  
  // CRITICAL FAILSAFE WATCHDOG: Disengage laser immediately if target tracking halts
  if (millis() - lastValid > LOST_TIMEOUT) {
    digitalWrite(LASER_PIN, LOW);
  }
}
