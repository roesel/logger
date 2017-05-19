#include <Sensirion.h>

const uint8_t dataPin1 =  3;              // SHT serial data 1
const uint8_t dataPin2 =  2;              // SHT serial data 2
const uint8_t sclkPin =  13;              // SHT serial clock
const uint8_t ledPin  = 13;              // Arduino built-in LED
const uint32_t TRHSTEP   = 5000UL;       // Sensor query period
const uint32_t BLINKSTEP =  250UL;       // LED blink period

Sensirion sht_1 = Sensirion(dataPin1, sclkPin);

uint16_t rawData_1;
float temperature_1;
float humidity_1;
float dewpoint_1;
byte measActive_1 = false;
byte measType_1 = TEMP;

Sensirion sht_2 = Sensirion(dataPin2, sclkPin);

uint16_t rawData_2;
float temperature_2;
float humidity_2;
float dewpoint_2;
byte measActive_2 = false;
byte measType_2 = TEMP;

byte ledState = 0;


unsigned long trhMillis = 0;             // Time interval tracking
unsigned long blinkMillis = 0;

void setup() {
    Serial.begin(9600);
    delay(15);                           // Wait >= 11 ms before first cmd
}

void loop() {
    unsigned long curMillis = millis();          // Get current time

    // Rapidly blink LED.  Blocking calls take too long to allow this.
    if (curMillis - blinkMillis >= BLINKSTEP) {  // Time to toggle the LED state?
        ledState ^= 1;
        digitalWrite(ledPin, ledState);
        blinkMillis = curMillis;
    }

    // Demonstrate non-blocking calls
    if (curMillis - trhMillis >= TRHSTEP) {      // Time for new measurements?
        measActive_1 = true;
        measType_1 = TEMP;
        measActive_2 = true;
        measType_2 = TEMP;
        sht_1.meas(TEMP, &rawData_1, NONBLOCK);      // Start temp measurement
        sht_2.meas(TEMP, &rawData_2, NONBLOCK);      // Start temp measurement
        trhMillis = curMillis;
    }
    if (measActive_1 && sht_1.measRdy()) {           // Note: no error checking
        if (measType_1 == TEMP) {                  // Process temp or humi?
            measType_1 = HUMI;
            temperature_1 = sht_1.calcTemp(rawData_1); // Convert raw sensor data
            sht_1.meas(HUMI, &rawData_1, NONBLOCK);  // Start humidity measurement
        }
        else {
            measActive_1 = false;
            humidity_1 = sht_1.calcHumi(rawData_1, temperature_1); // Convert raw sensor data
            dewpoint_1 = sht_1.calcDewpoint(humidity_1, temperature_1);
        }
    }
    if (measActive_2 && sht_2.measRdy()) {           // Note: no error checking
        if (measType_2 == TEMP) {                  // Process temp or humi?
            measType_2 = HUMI;
            temperature_2 = sht_2.calcTemp(rawData_2); // Convert raw sensor data
            sht_2.meas(HUMI, &rawData_2, NONBLOCK);  // Start humidity measurement
        }
        else {
            measActive_2 = false;
            humidity_2 = sht_2.calcHumi(rawData_2, temperature_2); // Convert raw sensor data
            dewpoint_2 = sht_2.calcDewpoint(humidity_2, temperature_2);
        }
    }

    // storing incoming command
    int command;

    // is a command available?
    if (Serial.available()>0) {
        // read a key-letter
        command = Serial.read();
        switch(command) {
            case 'L':
                logDataDict_1();
                break;
            case 'K':
                logDataDict_2();
                break;
        }
    }
}

void logDataDict_1() {
    Serial.print("{");
    
    Serial.print("\"sensor\":\"");
    Serial.print("1");
    Serial.print("\", ");

    Serial.print("\"temperature\":\"");
    Serial.print(temperature_1);
    Serial.print("\", ");

    Serial.print("\"humidity\":\"");
    Serial.print(humidity_1);
    Serial.print("\", ");

    Serial.print("\"dewpoint\":\"");
    Serial.print(dewpoint_1);
    Serial.print("\"");
    
    Serial.println("}");
}

void logDataDict_2() {
    Serial.print("{");
    
    Serial.print("\"sensor\":\"");
    Serial.print("2");
    Serial.print("\", ");

    Serial.print("\"temperature\":\"");
    Serial.print(temperature_2);
    Serial.print("\", ");

    Serial.print("\"humidity\":\"");
    Serial.print(humidity_2);
    Serial.print("\", ");

    Serial.print("\"dewpoint\":\"");
    Serial.print(dewpoint_2);
    Serial.print("\"");
    
    Serial.println("}");
}
