/*
  Gümüşdil Firmware v1.1
  Bu kod, Gümüşdil IDE ile Arduino arasında haberleşmeyi sağlar.
  
  Protokol:
  - L<pin>_<durum> : Dijital Yazma (Örn: L13_1 => Pin 13 HIGH)
  - O<pin>         : Dijital Okuma (Örn: O12   => Pin 12 Oku) -> Cevap: D<deger>
  - A<pin>_OKU     : Analog Okuma (Örn: A0_OKU => A0 Oku)    -> Cevap: A<deger>
  - PWM<pin>_<val> : Analog Yazma (Örn: PWM3_255)
  - S<pin>_<aci>   : Servo Yazma (Örn: S9_90)
*/

#include <Servo.h>

Servo servos[14]; // Pin sayisi kadar rezerv (Uno icin yeterli)
bool servoAttached[14] = {false};

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50); // Hızlı tepki için timeout düşük
  
  // Standart pin modları (Gerekirse dinamik yapılabilir ama şimdilik varsayılanlar)
  pinMode(13, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String komut = Serial.readStringUntil('\n');
    komut.trim(); // Boşlukları temizle
    
    islet(komut);
  }
}

void islet(String komut) {
  // L13_1 formatı (LED Yak/Söndür)
  if (komut.startsWith("L")) {
    int altTireIndex = komut.indexOf('_');
    if (altTireIndex > 1) {
      int pin = komut.substring(1, altTireIndex).toInt();
      int durum = komut.substring(altTireIndex + 1).toInt();
      pinMode(pin, OUTPUT); // Garanti olsun
      digitalWrite(pin, durum);
    }
  }
  // M13_1 formatı (Pin Mode) -> 0: INPUT, 1: OUTPUT, 2: INPUT_PULLUP
  else if (komut.startsWith("M")) {
    int altTireIndex = komut.indexOf('_');
    if (altTireIndex > 1) {
      int pin = komut.substring(1, altTireIndex).toInt();
      int mod = komut.substring(altTireIndex + 1).toInt();
      if (mod == 0) pinMode(pin, INPUT);
      else if (mod == 2) pinMode(pin, INPUT_PULLUP);
      else pinMode(pin, OUTPUT);
    }
  }
  // A0_OKU formatı (Analog Oku)
  else if (komut.startsWith("A") && komut.endsWith("_OKU")) {
    int altTireIndex = komut.indexOf('_');
    if (altTireIndex > 1) {
       int pinNum = komut.substring(1, altTireIndex).toInt();
       int val = analogRead(pinNum);
       Serial.println(val); 
    }
  }
  // S9_90 formatı (Servo)
  else if (komut.startsWith("S")) {
    int altTireIndex = komut.indexOf('_');
    if (altTireIndex > 1) {
      int pin = komut.substring(1, altTireIndex).toInt();
      int aci = komut.substring(altTireIndex + 1).toInt();
      
      if (pin >= 0 && pin < 14) {
        if (!servoAttached[pin]) {
          servos[pin].attach(pin);
          servoAttached[pin] = true;
        }
        servos[pin].write(aci);
      }
    }
  }
}
