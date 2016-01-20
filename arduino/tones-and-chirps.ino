#define OUT_PIN 8
#define LOWER 5000
#define HIGHER 30000
#define HIGHEST 50000

void setup() {
  pinMode(OUT_PIN,OUTPUT);
  pinMode(13,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  while(1) {
    if(Serial.available() >= 3) {
      int start = Serial.read();
      int end = Serial.read();
      int duration = Serial.read();
      digitalWrite(13,HIGH);
      linearSweep(1000 * start, 1000 * end, duration);
      digitalWrite(13,LOW);
    } 
  }
}

void not_loop() {
  linearSweep(30000,70000,5);
  delay(500);
}

void playTone(int freq, float duration, bool thenOff) {
  tone(OUT_PIN,freq,duration);
  delayMicroseconds(1000 * duration);
  if(thenOff) {
    noTone(OUT_PIN);
  }
}

void linearSweep(int start_freq, int end_freq, int duration) {
  int intervals = 30;
  float perDuration = float(duration) / intervals;
  for(int i = 0; i <= intervals; i++ ) {
    float f = start_freq + (end_freq - start_freq) * (float(i) / intervals);
    tone(OUT_PIN,f);
    delayMicroseconds(1000 * perDuration);
    noTone(OUT_PIN);
  }
  noTone(OUT_PIN);
}

