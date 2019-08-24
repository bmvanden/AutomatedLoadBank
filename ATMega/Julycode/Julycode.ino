
 /*                                                                            Load Bank Atmel Code
                                                                               EcoCar FC Team 
                                                                               Elizabeth Gierl
                                                                               Summer 2019                                                                          */

//Things left to do:
// Saftey thing 
// double check with Jaya code 
//Read more from PID library to make sure it is actually doing that I think I am doing
//add max fan speed
//add watch dog
//current sensor readings 

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
 Read_From_Atmega(); 
 AirStarve();

//if over current
 if (CurrentCurrent > 60){
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=100;
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
      Desired_Fan_Speed=100;
      //what number is max desired fan speed
      break;
    case 5:
      Serial.println("Over Temperature in control region"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=100;
      //what number is max desired fan speed
      break;
    case 6:
      Serial.println("Over Current"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=100;
      //what number is max desired fan speed
      break;
    case 7:
      Serial.println("Cell voltage is too high"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=100;
      break;
    case 8:
      Serial.println("Cell voltage is too low"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=100;
      break;
    case 9:
      Serial.println("Battery Voltage is too Low"); 
      DesiredCurrent=0;
      AirStarve_Set=0;
      Desired_Fan_Speed=100;
      break;
    case 10:
      AirStarve_Set=1;
      break;
    default: 
      Serial.println("Lost Communication"); 
    break;
  }
  
   
  //Fans:
double Setpoint1= 100; 
Input1= Desired_Fan_Speed;
Output1= Fan_Speed;


// Load Control 
double Setpoint= 100; 
Input= DesiredCurrent;
Output= CurrentCurrent;

}










//FUNCTIONS

void saftey_pin()  //interupt saftey pin        
{                   
   DesiredCurrent=0;
   AirStarve_Set=0;
   Desired_Fan_Speed=100;                              
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
