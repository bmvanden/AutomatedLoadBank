/*
 * Filename: PWM.ino
 * Title:    EcoCar - Automated Resistive Load Bank
 * Date:     March 31, 2019
 * Author:   Jaya Arora   jarora@ualberta.ca
 * Purpose:  Implementation of pulse width modulation and control of various aspects of the fuel cell
 */

#include <watchdogHandler.h>
#include <avr/power.h>
#include <avr/wdt.h>
#include <avr/sleep.h>
#include <PID_AutoTune_v0.h>
#include <PID_v1.h>
#include <Wire.h>

#define SLAVE_ADDRESS 0x08
#define F_CPU 16000000

// Global Variables:
int Battery_Voltage_Pin = A2;             // Battery connected to analog pin 2
int Battery_Val = 0;                      // Variable to store the Battery Voltage read value
int Battery_ValH = 0;                     // Battery Voltage High bit
int Battery_ValL = 0;                     // Battery Voltage Low bit

int FCell_Voltage_Pin = A1;               // FCell Voltage connected to analog pin 1
int FCell_VVal = 0;                       // Variable to store the FCell Voltage read value
int FCell_VValH = 0;                      // FCell Voltage High bit
int FCell_VValL = 0;                      // FCell Voltage Low bit

int FCell_Current_Pin = A0;               // FCell Current connected to analog pin 0
int FCell_CVal = 0;                       // Variable to store the FCell Current read value
int FCell = 0;                            // Variable to store the FCell Current in Conditioning/Polarization cycle
int FCell_CValH = 0;                      // FCell Current High bit
int FCell_CValL = 0;                      // FCell Current Low bit

int ASCheck = 0;                          // Checks to make sure Air Starve value is below the TOP value
int ASTrigger = 0;                        // Triggers to 1 if Air Starve Cycle is initiated
int Air_Starve_Pin = 7;                   // Air Starve Relay (Digital)
int AStarve_Val = 0;                      // Initialized air starve as value 0
int Safety_Pin = 2;                       // Safety Interrupt connected to Raspberry Pi
int Safety_Val = 1;                       // Variable to store Safety Interrupt
int Fans = 0;                             // Variable to store the final fan speed after comparing 2 speeds
int Fan_Pin = 6;                          // Ouput of fan speed to digital pin 6
int Fan1_speed = 0;                       // Variable to store the 1st fan speed
int Fan2_speed = 0;                       // Variable to store the 2nd fan speed
int Fan1_Val = 0;                         // Variable to map PWM speed
int Fan2_Val = 0;                         // Variable to map PWM speed

float Current = 0;                        // Value from 0-60Amps - received during Conditioning or Polarization Curve
int Conditioning_Pin = 10;                // Digital Pin connected to output to the fuel cell
int Conditioning_Val = 0;                 // Variable to store the Current mapped to TOP value
int receiveBuffer[9];                     // 9 byte data buffer for input from Raspberry pi
uint8_t keepCounted = 0;                  // Counter for Voltage and Current Values
int New_value = 5;                        // Variable to account for change in Conditioning/Polarization
int pin = 0;                              // trigger for conditioning/polarization
int change_val = 0;                       // Variable which changes to account for Proportionality difference in PID
int read_val = 0;                         // Mapped value read of FCell Current in Conditioning/Polarization

void setup(){
  pinMode(Air_Starve_Pin, OUTPUT);
  pinMode(Conditioning_Pin, OUTPUT); 
  pinMode(Fan_Pin, OUTPUT);
  
  //Intital read values from analog pins
  Battery_Val = analogRead(Battery_Voltage_Pin); 
  FCell_Voltage_Pin = analogRead(FCell_Voltage_Pin);
  FCell_Current_Pin = analogRead(FCell_Current_Pin);
  
  Serial.begin(9600);                     // start serial for output
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  PWM25kHzBegin();
  initAnalog();
}

void PWM25kHzBegin() {
  //Conditioning:
  TCCR1A = 0;
  TCCR1B = 0;
  OCR1A = 640; 
  OCR1B = 0;
  DDRB |= (1<<PINB2);
  TCCR1A |= (1<<COM1A1)|(1<<COM1B1)|(1<<WGM11)|(1<<WGM10);    //Non-inverting Mode - Clear OC1A/OC1B on Compare Match, Set at BOTTOM
  TCCR1B |= (1<<CS10)|(1<<WGM13)|(1<<WGM12); //prescalar 1    // 25kHz
  
  //Fans : 
  TCCR0A = 0;
  TCCR0B = 0;
  OCR0A = 0x0;
  PORTD |= (1<<PIND6);
  DDRD |= (1<<PIND6);
  TCCR0A |= (1<<COM0A1)|(1<<WGM00)|(1<<WGM01);                //Non-Inverting Mode - Clear OC0A on Compare Match, Set at BOTTOM
  TCCR0B |= (1<<CS01); //prescalar 1                          // 7.8kHz
}

void initAnalog(){
  ADMUX = (ADMUX | (1<<REFS0)) & ~(1<<REFS1);                 // Set analog reference to external A_ref
  ADCSRA |= (1<<ADEN) | (1<<ADPS2) | (1<<ADPS1) | (1<<ADPS0); // Enable analog to digital conversion. Set div/8 pre-scaler for ADC clock.
  DIDR0 |= (1<<ADC3D);                                        // Disable digital output on ADC3
  PRR &= ~(1<<PRADC);                                         // Turn off power reduction
  ADMUX &= 0xF0;                                              // Set ADC input to given parameter by clearing input selection bits, then setting to ADC3
  ADMUX |= 3;
}

void sendData(){                                        // Values sent to RPi through I2C - uses writeData function
  if (receiveBuffer[0] == 122) {
    writeData(values(1),values(2),values(3),values(4),values(5),values(6));
  }
}

void receiveData(int byteCount){                        // Values received from RPi through I2C
  int counter = 0;
  while(Wire.available()) {
    receiveBuffer[counter] = Wire.read();
    counter ++; 
  }
}

void writeData(char newDatafirst, char newDatasecond, char newDatathird, char newDatafourth, char newDatafifth, char newDatasixth) { // Writes to RPi
  char data[] = {receiveBuffer[0], newDatafirst, newDatasecond, newDatathird, newDatafourth, newDatafifth, newDatasixth};
  int dataSize = sizeof(data);
  Wire.write(data, dataSize);
}

int values(int keepCounted){
  if(keepCounted == 1){                                // Air Starve cycle - triggered every second
    ASCycle();
  }
  if(keepCounted == 1){
    return Battery_ValH;
  }
  else if(keepCounted == 2){
    return Battery_ValL;
  }
  else if(keepCounted == 3){
    return FCell_VValH;
  }
  else if(keepCounted == 4){
    return FCell_VValL;
  }
  else if(keepCounted == 5){
    return FCell_CValH;
  }
  else if(keepCounted == 6){
    keepCounted = 0;
    return FCell_CValL;
  }
}

void fanControl(){                                    // Fan speed control
  if(receiveBuffer[0] == 0){                          // Safety check - turn off load
    digitalWrite(Air_Starve_Pin,LOW); 
    OCR1B = 0;
    OCR0A = 0;
    return;
  }
  Fan1_Val = map(Fan1_speed, 0, 10, 0, 255);
  Fan2_Val = map(Fan2_speed, 0, 10, 0, 255);
  if (Fan1_Val >= Fan2_Val){
    Fans = Fan1_Val;
    OCR0A = Fans;
  }
  else{
    Fans = Fan2_Val;
    OCR0A = Fans;
  }
  Safety_Val = digitalRead(Safety_Pin);               // Safety check
  if (Safety_Val == 0){
    digitalWrite(Air_Starve_Pin,0);
    OCR1B = 0;
    OCR0B = 0;
  }
  return;
}

void ASCycle(){                                       // Air Starve - triggered every second
  if(receiveBuffer[0] == 0){                          // Safety check - turn off load
    digitalWrite(Air_Starve_Pin,LOW); 
    OCR1B = 0;
    OCR0A = 0;
    return;
  }
  if(ASTrigger == 1){
    if(ASCheck < 640){
      ASCheck = ASCheck + 2;
      OCR1B = ASCheck;
    }
    if(ASCheck == 640){
      AStarve_Val = 1;
      digitalWrite(Air_Starve_Pin, HIGH);
    }
    Safety_Val = digitalRead(Safety_Pin);             // Safety check
    if (Safety_Val == 0){
      digitalWrite(Air_Starve_Pin,0);
      OCR1B = 0;
      OCR0B = 0;
    }
    return;
  }
}

void Conditioning(){                                  // Controls the current output during conditioning/polarization through a PD control
  if(receiveBuffer[0] == 0){                          // Safety check - turn off load
    digitalWrite(Air_Starve_Pin,LOW); 
    OCR1B = 0;
    OCR0A = 0;
    return;
  }
  if(pin == 1){
    Safety_Val = digitalRead(Safety_Pin);             // Safety check
    if (Safety_Val == 0){
      digitalWrite(Air_Starve_Pin,0);
      OCR1B = 0;
      OCR0B = 0;
      return;
    }
    
    Conditioning_Val = floor(map(Current, 0, 60, 0, 640));
    FCell = analogRead(FCell_Current_Pin);
    read_val = floor(map(FCell,511,154,0,640));
    
    if(read_val < Conditioning_Val){                  // Need to increase the cell current
      if(Conditioning_Val-read_val >= 20){
        change_val = 5;
        New_value = Conditioning_Val + change_val;
        OCR1B = New_value;
        delay(100);
        return;
      }
      else if((Conditioning_Val-read_val<20) &&(Conditioning_Val-read_val >=10)){
        change_val = 2;
        New_value = Conditioning_Val + change_val;
        OCR1B = New_value;
        delay(100);
        return;
      }
      else if((Conditioning_Val-read_val<10) &&(Conditioning_Val-read_val > 0)){
        change_val = 1;
        New_value = Conditioning_Val + change_val;
        OCR1B = New_value;
        delay(100);
        return;
      }
    }
    
    else if(read_val > Conditioning_Val){             // Need to decrease the cell current
      if(read_val-Conditioning_Val >= 20){
        change_val = 5;
        New_value = Conditioning_Val - change_val;
        OCR1B = New_value;
        delay(100);
        return;
      }
      else if((read_val-Conditioning_Val<20) &&(read_val-Conditioning_Val >=10)){
        change_val = 2;
        New_value = Conditioning_Val - change_val;
        OCR1B = New_value;
        delay(100);
        return;
      }
      else if((read_val-Conditioning_Val<10) &&(read_val-Conditioning_Val > 0)){
        change_val = 1;
        New_value = Conditioning_Val - change_val;
        OCR1B = New_value;
        delay(100);
        return;
      }
    }
    
    else if(read_val == Conditioning_Val){          // Output either one
      OCR1B = Conditioning_Val;
      New_value = Conditioning_Val;
//      pin = 0;
      return;
    } 
  }
}

void loop(){
  Battery_Val = int(analogRead(A2));                // Range: 0-15V (Reads 0-1023)
  Battery_ValH = Battery_Val >> 8;                  // High bits of the battery voltage
  Battery_ValL = Battery_Val - (Battery_ValH << 8); // Low bits of the battery voltage
  
  FCell_VVal = int(analogRead(A1));                 // Range: 0-46V (Reads 0-1023)
  FCell_VValH = FCell_VVal >> 8;                    // High bits of the cell voltage
  FCell_VValL = FCell_VVal - (FCell_VValH << 8);    // Low bits of the cell voltage
  
  FCell_CVal = int(analogRead(A0));                 // Range: 0-60A (Reads 0-1023)
  FCell_CValH = FCell_CVal >> 8;                    // High bits of the cell current
  FCell_CValL = FCell_CVal - (FCell_CValH << 8);    // Low bits of the cell current
  
  if(receiveBuffer[0] == 0){                        // Safety check - turn off load
    digitalWrite(Air_Starve_Pin,LOW); 
    OCR1B = 0;
    OCR0A = 0;
  }
  else if(receiveBuffer[0] == 121){                 // Air Starve Cycle
      ASTrigger = 1;
      ASCycle();       
  }
  else if(receiveBuffer[0] == 123){                 // Fan Control
    Fan1_speed = receiveBuffer[1];
    Fan2_speed = receiveBuffer[2];
    fanControl();
  }
  else if((receiveBuffer[0] > 0) && (receiveBuffer[0] < 121)){ // Current Output for Conditioning and Polarization Curve
    pin = 1;
    Current = receiveBuffer[0]/2;
    Conditioning();
  }
  Safety_Val = digitalRead(Safety_Pin);             // Safety check - checks pin position
  if (Safety_Val == 0){
    digitalWrite(Air_Starve_Pin,0);
    OCR1B = 0;
    OCR0A = 0;
  }
}
