
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

char c[]={223,8,221};


//MAIN LOOP
void loop() {
  
//Code for testing:
  char  Atmega_Status=2; //1 byte
  char Pi_Status= 23; // 1 byte
  int FC_Volt=46; //2 bytes
  int Battery_Volt=30; //2 bytes
  char Fan_Speed=2;//1 byte
  char CurrentCurrent=40;//1 bytes
  char DesiredCurrent=3; //1 byte
 
//Call functions:  
char Read_Inputs = Read_From_Atmega();
}


//FUNCTIONS
char Read_From_Atmega() {
  
  char  Atmega_Status=2;//how should we collect this?
  char FC_Volt=analogRead(A1);
  char Battery_Volt=analogRead(A2);
  char CurrentCurrent=analogRead(A0);
  char output[]= {Atmega_Status,FC_Volt,Battery_Volt,CurrentCurrent}; // would need to convert it to char all by bit casting 
  return output;
  
}

void Read_From_Pi(int howMany) {

  int i=0;
while ( Wire.available()) { // loop through all but the last
    c[i] = Wire.read(); // receive byte as a character
    Serial.print(c[i]);
    i++;      
    }
  
}
  
void Write_to_Pi() {  
//Convert to char 
char FC_Volt=4;
char Battery_Volt=3;
char Atmega_Status=4;
char CurrentCurrent=20;
char testvalue=5;
  char data[] = {testvalue,testvalue, testvalue,c[1],c[2],c[3],testvalue,testvalue};
  Wire.write(data); 
  //Serial.println(data); 
}




void Respond_To_States(){
//DO LATER
}
