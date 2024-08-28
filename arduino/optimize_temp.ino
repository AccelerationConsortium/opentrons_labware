const int pwmPin = 9;       // PWM output pin connected to the heating pad
const int thermistorPin = A0; // analog input pin connected to the thermistor

void setup() {
  Serial.begin(9600);
  pinMode(pwmPin, OUTPUT);
  pinMode(thermistorPin, INPUT);
}

void loop() {
  while (Serial.available() == 0){
    continue;
  }

  char funcnum = Serial.read();
  switch(funcnum){
    case 0x01:
      {applyPWM();
      break;}
    case 0x02:
      {readTemp();
      break;}
    default:
      break;
  }
}

void applyPWM(){
  char pwm = Serial.read();
  analogWrite(pwmPin, pwm);
}

void readTemp(){
  unsigned int reading = 0;
  for (int i=0; i<0xff; i++){
    reading += analogRead(thermistorPin);
  }

  Serial.write(reading>>8);
  Serial.write(reading & 0xff);
}
