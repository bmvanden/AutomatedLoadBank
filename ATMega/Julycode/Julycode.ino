
 /*                                                                            Load Bank Atmel Code
                                                                               EcoCar FC Team 
                                                                               Elizabeth Gierl
                                                                               Summer 2019                                                                          */

//Things left to do:
// Saftey thing
//Signal bit 
//make sure Air starve thing is correct..
// double check with Jaya code 

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
  char  Atmega_Status=2; //1 byte
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
 Read_From_Atmega(); 
   
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
