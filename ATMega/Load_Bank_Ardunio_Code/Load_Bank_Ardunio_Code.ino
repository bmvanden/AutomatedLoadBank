
 /*                                                                            Load Bank Atmel Code
                                                                               EcoCar FC Team 
                                                                               Elizabeth Gierl
                                                                               Summer 2019                                                                          */



#include <Wire.h>
#define SLAVE_ADDRESS 0x08

void setup() { 
 Wire.begin(SLAVE_ADDRESS);        // join i2c bus with address #8
 Wire.onRequest(Write_to_Pi); // register event
 Wire.onReceive(Read_From_Pi); // register event
 Serial.begin(9600);  
}


//setup global varaibles 
  char  Atmega_Status=2; //1 byte
  char Pi_Status= 23; // 1 byte 
  char FC_Volt_low=46; //1 bytes 8 bits
  char FC_Volt_high=16; //1 byte 2 bits
  char Battery_Volt_low=30; //1 bytes 8 bits
  char Battery_Volt_high=30; //1 bytes two bits
  char Fan_Speed=2;//1 byte
  char CurrentCurrent=40;//1 bytes
  char DesiredCurrent=3; //1 byte
  char c[]={223,8,221,40};
  char Read_Inputs[]={0,0,0,223,8,221,40};
  char output_pi[]={0,1, 1, 1}; 


//MAIN LOOP
void loop() {
 
//Call functions:  
  


// Respond to states:
  //Make a plan for response to changes of states:

//Read fan speed and adjust fan PWM value accordingly (5 speeds?) low , low medium, medium, medium high, high temp?
//Conditioning : Recieve a max current from the pi code? Then 1A stepsize? to the max every one min
//Air starve: Trigger other output ?
//Battery Voltage? Anything but reading it?
// Saftey Check from Jayas Code?


//pin mapping:
//

  
  //Monday:Solder other board + figure out to call functions
  //Tuesday: Put Code on git 

}


//FUNCTIONS
void Read_From_Atmega() {
  
  char  Atmega_Status=2;//how should we collect this?
  int FC_Volt=analogRead(A1);
  int Battery_Volt=analogRead(A2);
  FC_Volt_low=lowByte(FC_Volt);
  FC_Volt_high=highByte(FC_Volt);
  Battery_Volt_low=lowByte(Battery_Volt);
  Battery_Volt_high=highByte(Battery_Volt);
  char CurrentCurrent=analogRead(A0);
  char Read_Inputs[]= {0,Atmega_Status,FC_Volt_low,FC_Volt_high,Battery_Volt_low,Battery_Volt_high,CurrentCurrent}; 
}

void Read_From_Pi(int howMany) {
  
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
  
  char output_pi[]={0,Pi_Status, Fan_Speed, DesiredCurrent}; 
  
}
  
void Write_to_Pi() {  
  char data[] ={0,Atmega_Status,FC_Volt_low,FC_Volt_high,Battery_Volt_low,Battery_Volt_high,CurrentCurrent}; 
  Wire.write(data); 
  Serial.println(data); 
}
