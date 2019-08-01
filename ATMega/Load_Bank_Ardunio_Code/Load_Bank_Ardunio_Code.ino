
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
  char CurrentCurrent=40;//1 bytes
  char DesiredCurrent=3; //1 byte
  char c[]={223,8,221,40};
  char Read_Inputs[]={0,0,0,223,8,221,40};
  char output_pi[]={0,1, 1, 1}; 
  char Temperature= 10; 
  char Fan_Speed=OCR0A;
  char AirStarve_Set=0;
  char Conditioning_Set=0;
  char Conditioning_Value=0;
  char Resistance=OCR1B;



//MAIN LOOP
void loop() {

  //variables 
  char low=10;
  char low_medium=20;
  char medium=30;
  char medium_high=40;
  char high=60;

//Call functions:  

// Add conditions in which Airstarve vs different types of pol curve + conditioning is called
//Conditioning : Recieve a max current from the pi code? Then 1A stepsize? to the max every one min
//Air starve: Trigger other output ?
//Battery Voltage? Anything but reading it?
// Saftey Check from Jayas Code?

  
  
  //Fans:
  if (Temperature > low) {
    Fan_Speed=0;
   }
  else if (low < Temperature > low_medium) {
    Fan_Speed=5;
   }
  else if (low_medium < Temperature > medium) {
    Fan_Speed==20;
   }
  else if (medium < Temperature > medium_high) {
    Fan_Speed==40;
   }
  else if (medium_high < Temperature > high) {
    Fan_Speed==60;
   }
  else if (high < Temperature) {
    Fan_Speed== 100;
   }


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


void AirStarve(){

  if(AirStarve_Set==1){
    digitalWrite(13, HIGH);
  }
  
  else{
    digitalWrite(13, LOW);
  }

}


void Conditioning(){
  if (Conditioning_Set==1){
     Resistance==Conditioning_Value;
  }
  else{
     Resistance==0;
  }
  
}

void PolCurve(){

if (CurrentCurrent < DesiredCurrent){
  Resistance = Resistance--;
  
}

else if (CurrentCurrent > DesiredCurrent){
  Resistance = Resistance++;
}


else if (CurrentCurrent == DesiredCurrent){
  Resistance = Resistance;
}


}
