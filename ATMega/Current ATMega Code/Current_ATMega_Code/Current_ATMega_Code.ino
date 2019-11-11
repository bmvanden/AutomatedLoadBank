
 /*                                                                            Load Bank Atmel Code
                                                                               EcoCar FC Team 
                                                                               Elizabeth Gierl
                                                                               Spring Summer 2019                                                                          */

#include <Wire.h>
#define SLAVE_ADDRESS 0x08
#include <PID_v1.h>
#include <avr/wdt.h>

// PID CODES   
//Specify the links and initial tuning parameters 
double Setpoint, Input, Output;
PID loadPID(&Input, &Output, &Setpoint, 2, 5, 1, DIRECT);

// PID needs doubles is this a problem?
double Setpoint1, Input1, Output1;
PID fansPID(&Input1, &Output1, &Setpoint1, 2, 5, 1, DIRECT);

//GLOBAL VARIABLES
  char c[]={0,223,8,221};
  char  Atmega_Status=20; 
  char Pi_Status= 23;
  int FC_Volt=46; 
  int Battery_Volt=30; 
  char Desired_Temperature=1;
  char Load_Temperature= 1;
  char Control_Temperature=2;
  int CurrentCurrent=40;
  char DesiredCurrent=3; 
  char CellVoltageLow=5;
  char CellVoltageHigh=5;
  char BatteryVoltageLow=5;
  char BatteryVoltageHigh=5;
  char CellCurrentLow=5;
  char CellCurrentHigh=5;
  char AirStarve_Set=0;
  char Current_Temperature=80;


void setup() { 
 //I2C Setup
 Wire.begin(SLAVE_ADDRESS);        // join i2c bus with address #8
 Wire.onRequest(Write_to_Pi); // register event
 Wire.onReceive(Read_From_Pi); // register event
 //Serial setup
 Serial.begin(9600);  
  //turn the PID on
 fansPID.SetMode(AUTOMATIC);
// loadPID.SetMode(AUTOMATIC);
 pinMode(13, OUTPUT); //for airstarve relay
 //watchdog setup
 watchdogSetup();
// analogReference(EXTERNAL); //CONNECT 3.3 line from atmel chip to AREF MAY NEED TO DO THIS! 
Serial.print(3);
}



//MAIN LOOP
void loop() { 
  Serial.print(5);
 //Call functions
 attachInterrupt(digitalPinToInterrupt(2), saftey_pin, FALLING);
 PWM25kHzBegin();
 initAnalog();
 Read_From_Atmega(); 
 AirStarve();

// over current saftey check
 if (CurrentCurrent > 60){
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Temperature=40;
      Atmega_Status=6;
      //what number is max desired fan speed 
 }

Pi_Status=0;
switch (Pi_Status) {
    case 0:
      Serial.println("Booting Up"); 
      Atmega_Status=0;
      break;
    case 1:
      Serial.println("Establishing I2C"); 
      break;
    case 2:
      Serial.println("Communication Established"); 
      Atmega_Status=2; 
      break;
    case 3:
      Serial.println("Normal Operation"); 
      break;
    case 4:
      Serial.println("Over Temperature in load region"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Temperature=40;
      break;
    case 5:
      Serial.println("Over Temperature in control region"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Temperature=40;
      break;
    case 6:
      Serial.println("Over Current"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Temperature=40;
      break;
    case 7:
      Serial.println("Cell voltage is too high"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Temperature=40;
      break;
    case 8:
      Serial.println("Cell voltage is too low"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Temperature=40;
      break;
    case 9:
      Serial.println("Battery Voltage is too Low"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Temperature=40;
      break;
    case 10:
      AirStarve_Set=1;
      break;
    default: 
      Serial.println("Lost Communication"); 
    break;
  }
  
Load_Temperature=140;
Control_Temperature=10;

//Fans:
//if the temperature is 50 degrees, a value of 100 is sent from the pi 
//max temperature is 85 degrees 
if (Load_Temperature > 140){
  Current_Temperature=Load_Temperature;
}
else if (Control_Temperature >140){
  Current_Temperature=Control_Temperature ;
}
else{
  Current_Temperature= ((Control_Temperature+Load_Temperature)/2);
}

Serial.print(1);
Serial.print(Output1);
Setpoint1= Desired_Temperature;
Input1= Current_Temperature;
fansPID.Compute();
Serial.print(Output1);
analogWrite(12,Output1);

//The PID controller is designed to vary its output within a given range. By default this range is 0-255:

 Load Control
loadPID.SetOutputLimits(0, 640);
Setpoint= DesiredCurrent; 
Input= CurrentCurrent;
loadPID.Compute();
OCR1B=Output; 

}







//FUNCTIONS:

void PWM25kHzBegin() {
  //Conditioning:
  TCCR1A = 0;
  TCCR1B = 0;
  OCR1A = 640; 
  OCR1B = 0;
  DDRB |= (1<<PINB2);
  TCCR1A |= (1<<COM1A1)|(1<<COM1B1)|(1<<WGM11)|(1<<WGM10);    //Non-inverting Mode - Clear OC1A/OC1B on Compare Match, Set at BOTTOM
  TCCR1B |= (1<<CS10)|(1<<WGM13)|(1<<WGM12); //prescalar 1    // 25kHz
}

void initAnalog(){
  ADMUX = (ADMUX | (1<<REFS0)) & ~(1<<REFS1);                 // Set analog reference to external A_ref
  ADCSRA |= (1<<ADEN) | (1<<ADPS2) | (1<<ADPS1) | (1<<ADPS0); // Enable analog to digital conversion. Set div/8 pre-scaler for ADC clock.
  DIDR0 |= (1<<ADC3D);                                        // Disable digital output on ADC3
  PRR &= ~(1<<PRADC);                                         // Turn off power reduction
  ADMUX &= 0xF0;                                              // Set ADC input to given parameter by clearing input selection bits, then setting to ADC3
  ADMUX |= 3;
}

void watchdogSetup(void)
{
  // set it so reset is enabled after two seconds without any interrupts
  cli(); // disable all interrupts
  wdt_reset(); // reset the WDT timer
  /*
   WDTCSR configuration:
   WDIE = 1: Interrupt Enable
   WDE = 1 :Reset Enable
   WDP3 = 0 :For 2000ms Time-out
   WDP2 = 1 :For 2000ms Time-out
   WDP1 = 1 :For 2000ms Time-out
   WDP0 = 1 :For 2000ms Time-out
  */
  
  // Enter Watchdog Configuration mode:
  WDTCSR |= (1<<WDCE) | (1<<WDE);
  // Set Watchdog settings:
   WDTCSR = (1<<WDE) | (0<<WDP3) | (1<<WDP2) | (1<<WDP1) | (1<<WDP0);
  sei();
}

void saftey_pin()  //interupt saftey pin        
{                   
   DesiredCurrent=0;
   AirStarve_Set=0;
   Desired_Temperature=40;                            
   Serial.println("Saftey Button Interrupt");
}

void  Read_From_Atmega() {
  char  Atmega_Status=2;//how should we collect this?
  int FC_Volt=analogRead(A1);
  int Battery_Volt=analogRead(A2);
  int CurrentCurrent=analogRead(A0);
  //char Fan_Speed=????
  CurrentCurrent=(31.25)*(CurrentCurrent)+140.63;
  //^this could be further varified for higher accuracy

  //if over current
 if (CurrentCurrent > 60){
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Temperature=20;
      Atmega_Status=6;
      //what number is max desired fan speed 
 }
 
  char CellVoltageLow=lowByte(FC_Volt);
  char CellVoltageHigh=highByte(FC_Volt);
  char BatteryVoltageLow=lowByte(Battery_Volt);
  char BatteryVoltageHigh=highByte(Battery_Volt);
  char CellCurrentLow= lowByte(CurrentCurrent);
  char CellCurrentHigh= highByte(CurrentCurrent);
}

void Read_From_Pi(int howMany) {
  int i=0;
while ( Wire.available()) { // loop through all but the last
    c[i] = Wire.read(); // receive byte as a character
    Serial.print(c[i]);
    i++;      
    }
  Pi_Status=c[1];
  Desired_Temperature=c[2];
  Load_Temperature=c[3];
  Control_Temperature=c[4];
  DesiredCurrent=c[5];
  wdt_reset();

}
  
void Write_to_Pi() {  
//c[0] always gives a bad value and cannot be used
 char badvalue=5;
 char data[] ={badvalue,Atmega_Status,CellCurrentHigh, CellCurrentLow, CellVoltageHigh,CellVoltageLow,BatteryVoltageHigh,BatteryVoltageLow};
 Wire.write(data); 
}


void AirStarve(){
  if(AirStarve_Set==1){
    digitalWrite(13, HIGH);
  }
  else{
    digitalWrite(13, LOW);
  }
}
