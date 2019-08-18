
 /*                                                                            Load Bank Atmel Code
                                                                               EcoCar FC Team 
                                                                               Elizabeth Gierl
                                                                               Summer 2019                                                                          */



//pin mapping:
// Pol Curve + Conditioning: Pin 16 (PB2: SS/OC1B/PCINT2)
//Air Starve Relay: PD7 (PCINT23/AIN1)
// PWM for fans PD6 (PCINT22/OC0A/AIN0)

#include <Wire.h>
#define SLAVE_ADDRESS 0x08
#include <PID_v1.h>


//setup global varaibles 
  char  Atmega_Status=2; //1 byte
  char Pi_Status= 23; // 1 byte 
  char CellVoltageLow=46; //1 bytes 8 bits
  char CellVoltageHigh=16; //1 byte 2 bits
  char BatteryVoltageLow=30; //1 bytes 8 bits
  char BatteryVoltageHigh=30; //1 bytes two bits
  char CurrentCurrent=40;//1 bytes
  char DesiredCurrent=3; //1 byte
  char c[]={223,8,221,40};
  char Read_Inputs[]={0,0,0,223,8,221,40};
  char output_pi[]={0,1, 1, 1}; 
  char Fan_Speed=OCR0A;
  char Desired_Fan_Speed=2;
  char AirStarve_Set=0;
  char Conditioning_Set=0;
  char Conditioning_Value=0;
  char Resistance=OCR1B;
  char CellCurrentLow;
  char CellCurrentHigh;
  

  
  
//Specify the links and initial tuning parameters
double Setpoint, Input, Output;
PID loadPID(&Input, &Output, &Setpoint, 2, 5, 1, DIRECT);
// PID needs doubles is this a problem?


double Setpoint1, Input1, Output1;
PID fansPID(&Input1, &Output1, &Setpoint1, 2, 5, 1, DIRECT);
// PID needs doubles is this a problem?

void setup() { 
 Wire.begin(SLAVE_ADDRESS);        // join i2c bus with address #8
 Wire.onRequest(Write_to_Pi); // register event
 Wire.onReceive(Read_From_Pi); // register event
 Serial.begin(9600);  
 //turn the PID on
 fansPID.SetMode(AUTOMATIC);
 loadPID.SetMode(AUTOMATIC);
}





//MAIN LOOP
void loop() {

  //variables 
  char low=10;
  char low_medium=20;
  char medium=30;
  char medium_high=40;
  char high=60;

//Call functions:  
char Read_Inputs = Read_From_Atmega();

Read_From_Atmega();

// Add conditions in which Airstarve vs different types of pol curve + conditioning is called
//Conditioning : Recieve a max current from the pi code? Then 1A stepsize? to the max every one min
//Air starve: Trigger other output ?
//Battery Voltage? Anything but reading it?
// Saftey Check from Jayas Code?
 
  
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

char Read_From_Atmega() {
  
  char  Atmega_Status=2;//how should we collect this?
  int FC_Volt=analogRead(A1);
  int Battery_Volt=analogRead(A2);
  
  CellVoltageLow=lowByte(FC_Volt);
  CellVoltageHigh=highByte(FC_Volt);
  BatteryVoltageLow=lowByte(Battery_Volt);
  BatteryVoltageHigh=highByte(Battery_Volt);
  CellCurrentLow= lowByte(CurrentCurrent);
  CellCurrentHigh= highByte(CurrentCurrent);
  //add thisread!  Fan_Speed=; 
  
  char CurrentCurrent=analogRead(A0);
  char Read_Inputs[]= {0,Atmega_Status,CellCurrentHigh, CellCurrentLow, CellVoltageHigh,CellVoltageLow,BatteryVoltageHigh,BatteryVoltageLow};
  return Read_Inputs;
}

char Read_From_Pi(int howMany) {
  
  int i=0;
  while ( Wire.available()) { // loop through all but the last
      c[i] = Wire.read(); // receive byte as a character
      Serial.print(c[i]);
      i++;      
      }
  
  c[0]=0;
  Pi_Status=c[1];
  Fan_Speed=c[2];
  DesiredCurrent=c[3];
  
  char output_pi[]={0,Pi_Status, Desired_Fan_Speed, DesiredCurrent}; 
  
}




  
void Write_to_Pi() {  
  Wire.write(Read_Inputs); 
}




void AirStarve(){

  if(AirStarve_Set==1){
    digitalWrite(13, HIGH);
  }
  
  else{
    digitalWrite(13, LOW);
  }

}
