
 /*                                                                            Load Bank Atmel Code
                                                                               EcoCar FC Team 
                                                                               Elizabeth Gierl
                                                                               Summer 2019                                                                          */

//Things left to do:
//add watch dog
//current sensor readings 
// double check with Jaya code 
//done!

#include <Wire.h>
#define SLAVE_ADDRESS 0x08
#include <PID_v1.h>

// TEST THESE PID CODES   
//Specify the links and initial tuning parameters 
double Setpoint, Input, Output;
PID loadPID(&Input, &Output, &Setpoint, 2, 5, 1, DIRECT);
// PID needs doubles is this a problem?


double Setpoint1, Input1, Output1;
PID fansPID(&Input1, &Output1, &Setpoint1, 2, 5, 1, DIRECT);


void setup() { 
 Wire.begin(SLAVE_ADDRESS);        // join i2c bus with address #8
 Wire.onRequest(Write_to_Pi); // register event
 Wire.onReceive(Read_From_Pi); // register event
 Serial.begin(9600);  
  //turn the PID on
 fansPID.SetMode(AUTOMATIC);
 loadPID.SetMode(AUTOMATIC);
}

char c[]={223,8,221};
//Code for testing:
  char  Atmega_Status=20; //1 byte
  char Pi_Status= 23; // 1 byte
  int FC_Volt=46; //2 bytes
  int Battery_Volt=30; //2 bytes
  char Fan_Speed=2;//1 byte
  char Desired_Fan_Speed=9;
  int CurrentCurrent=40;//1 bytes
  char DesiredCurrent=3; //1 byte
  char CellVoltageLow=5;
  char CellVoltageHigh=5;
  char BatteryVoltageLow=5;
  char BatteryVoltageHigh=5;
  char CellCurrentLow=5;
  char CellCurrentHigh=5;
  char AirStarve_Set=0;


//MAIN LOOP

void loop() { 
 //Call functions
 attachInterrupt(digitalPinToInterrupt(2), saftey_pin, FALLING);
 PWM25kHzBegin();
 initAnalog();
 Read_From_Atmega(); 
 AirStarve();

//if over current
 if (CurrentCurrent > 60){
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=250;
      Atmega_Status=6;
      //what number is max desired fan speed 
 }

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
      Desired_Fan_Speed=250;
      //what number is max desired fan speed
      break;
    case 5:
      Serial.println("Over Temperature in control region"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=250;
      //what number is max desired fan speed
      break;
    case 6:
      Serial.println("Over Current"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=250;
      //what number is max desired fan speed
      break;
    case 7:
      Serial.println("Cell voltage is too high"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=250;
      break;
    case 8:
      Serial.println("Cell voltage is too low"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=250;
      break;
    case 9:
      Serial.println("Battery Voltage is too Low"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=250;
      break;
    case 10:
      AirStarve_Set=1;
      break;
    default: 
      Serial.println("Lost Communication"); 
    break;
  }
  
 
//Fans:
Setpoint1= Desired_Fan_Speed;
Input1= Fan_Speed;
fansPID.Compute();
analogWrite(12,Output);
//The PID controller is designed to vary its output within a given range. By default this range is 0-255:

// Load Control
loadPID.SetOutputLimits(0, 640);
Setpoint= DesiredCurrent; 
Input= CurrentCurrent;
loadPID.Compute();
OCR1B=Output; 

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

}

void initAnalog(){
  ADMUX = (ADMUX | (1<<REFS0)) & ~(1<<REFS1);                 // Set analog reference to external A_ref
  ADCSRA |= (1<<ADEN) | (1<<ADPS2) | (1<<ADPS1) | (1<<ADPS0); // Enable analog to digital conversion. Set div/8 pre-scaler for ADC clock.
  DIDR0 |= (1<<ADC3D);                                        // Disable digital output on ADC3
  PRR &= ~(1<<PRADC);                                         // Turn off power reduction
  ADMUX &= 0xF0;                                              // Set ADC input to given parameter by clearing input selection bits, then setting to ADC3
  ADMUX |= 3;
}







//FUNCTIONS

void saftey_pin()  //interupt saftey pin        
{                   
   DesiredCurrent=0;
   AirStarve_Set=0;
   Desired_Fan_Speed=250;                              
   Serial.println("Saftey Button Interrupt");
}

void  Read_From_Atmega() {
  char  Atmega_Status=2;//how should we collect this?
  int FC_Volt=analogRead(A1);
  int Battery_Volt=analogRead(A2);
  int CurrentCurrent=analogRead(A0);
   //add thisread!  Fan_Speed=;
  
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
  Desired_Fan_Speed=c[2];
  DesiredCurrent=c[3];
}
  
void Write_to_Pi() {  
//Convert to char 
 char testvalue=5;
 //char data[] = {testvalue,testvalue, testvalue,c[1],c[2],c[3],testvalue,testvalue};
 char data[] ={testvalue,Atmega_Status,CellCurrentHigh, CellCurrentLow, CellVoltageHigh,CellVoltageLow,BatteryVoltageHigh,BatteryVoltageLow};
 Wire.write(data); 
  //Serial.println(data); 
}


void AirStarve(){
  if(AirStarve_Set==1){
    digitalWrite(13, HIGH);
  }
  else{
    digitalWrite(13, LOW);
  }
}
