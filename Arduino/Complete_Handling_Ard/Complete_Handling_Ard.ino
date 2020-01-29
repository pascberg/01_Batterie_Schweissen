#include <Stepper.h>
#include "Control.h"
#include "Nema17.h"
#include "ContactSwitch.h"
#include "BJY48.h"
#include "OnOff.h"
#include "myStepper.h"
#define size(array) (sizeof(array) / sizeof(array[0]))

//Config variables
const float Pi = 3.14159;
Control* MyControl;
//Types
BJY48 *Bjy48[5];
Nema17 *NEMA17Pos;
Nema17 *NEMA17Ali;
Nema17 *NEMA17Arr;
Nema17 *NEMA17Vac;
myStepper *NEMA17Test;
OnOff *ValveAlignment;
OnOff *ValveWelding;
OnOff *ValveVacuum;
OnOff *PumpVacuum;
OnOff *Magnets;

Contactswitch *CsPos[2];
Contactswitch *CsAli[2];
Contactswitch *CsArr[2];
Contactswitch *CsVac[1];
Contactswitch *PsVac[1];
//Pins & Direction
const int stepsPerRevBJY48 = 2048; //Motorvariable how many steps needed for one revolution
const int rolePerMinBJY48 = 15; //Motor speed, max 19 rounds per Minute
int pinsBJY48[size(Bjy48)][4] = {{52, 50, 48, 46}, {44, 42, 40, 38}, {36, 34, 32, 30}, {28, 26, 24, 22}, {29, 27, 25, 23}};
int pinsNEMA17Pos[][3] = {{35, 45, 47}, {35, 51, 53}};
bool dirNEMA17Pos[] = {true, false};
int pinsNEMA17Ali[1][3] = {{35, 39, 41}};
bool dirNEMA17Ali[] = {false};
int pinsNEMA17Arr[][3] = {{35, 45, 47}, {35, 51, 53}};
bool dirNEMA17Arr[] = {true, false};
int pinsNEMA17Vac[][3] = {{35, 39, 41}};
bool dirNEMA17Vac[] = {true};
//Valve Config
int pinValveAlignment = 55;
int pinValveWelding = 54;
int pinValveVacuum = 55;
int pinPumpVacuum = 6;
int pinMagnets = 56;
int pinBuzzer = 12;
//Contactswitch Config
int pinCsPos[size(CsPos)] = {A6, A5};
int pinCsAli[size(CsAli)] = {A7, 0};
int pinCsArr[size(CsArr)] = {A6, 0};
int pinCsVac[size(CsVac)] = {A5};
int pinPsVac[size(PsVac)] = {A3};

//Functions
bool parseTask(String massage[]) {
  //Function to Parse a Massage and execute the Orders
  //Input: Massage [String Type, String Name, String Order, String Data]
  String Type = massage[0];
  String Name = massage[1];
  String Order = massage[2];
  String Data = massage[3];
  String s = Type + " " + Name + " "  + Order + " " + Data;
  Serial.println(s); //just sends massage back for checking
  //let the arduino wait until it returns complete
  if (Order == "wait") delay(Data.toInt());
  if (Type == "Motor") {
    Nema17 *nema17 = nullptr;
    BJY48 *BJy48 = nullptr;
    myStepper *stepperTest = nullptr;
    //assign right type and task
    if (Name == "Nema17Pos") nema17 = NEMA17Pos;
    if (Name == "Nema17Ali") nema17 = NEMA17Ali;
    if (Name == "48BJY28 1") BJy48 = Bjy48[0];
    if (Name == "48BJY28 2") BJy48 = Bjy48[1];
    if (Name == "48BJY28 3") BJy48 = Bjy48[2];
    if (Name == "48BJY28 4") BJy48 = Bjy48[3];
    if (Name == "48BJY28 5") BJy48 = Bjy48[4];
    if (Name == "Nema17Arr") nema17 = NEMA17Arr;
    if (Name == "Nema17Vac") nema17 = NEMA17Vac;
    if (Name == "Nema17Test") stepperTest = NEMA17Test;
    if (nema17 != nullptr) {
      if (Order == "moveTo") nema17->moveTo(Data.toInt());
      if (Order == "moveSteps") nema17->moveSteps(Data.toInt());
      if (Order == "position") Serial.println(nema17->currentPosition());
      if (Order == "setSpeed") nema17->setSpeed(Data.toInt());
      if (Order == "setAcceleration") nema17->setAccel(Data.toInt());
      if (Order == "reset") nema17->reset();
    }
    if (BJy48 != nullptr) {
      if (Order == "moveSteps") BJy48->steps(Data.toInt());
      if (Order == "moveRad") BJy48->moveRad(Data.toFloat());
      if (Order == "reset") BJy48->steps(-BJy48->stepsMade());
    }
    if (stepperTest != nullptr) {
      stepperTest->onOff(true);
      if (Order == "moveSteps") stepperTest->steps(Data.toInt());
      if (Order == "reset") stepperTest->reset();
      stepperTest->onOff(false);
    }
  }
  if (Type == "OnOff") {
    OnOff *onOff;
    if (Name == "PistonAli") onOff = ValveAlignment;
    if (Name == "PistonPos") onOff = ValveWelding;
    if (Name == "Magnets") onOff = Magnets;
    if (Name == "Vacuum") onOff = ValveVacuum;
    if (Name == "Pump") onOff = PumpVacuum;
    if (Order == "set") {
      if (Data == "On") onOff->on();
      if (Data == "Off") onOff->off();
    }
    if (Order == "reset") onOff->off();

  }
  return true;
}
void setup() {
  //setup for all classes and pins for the handling
  MyControl = new Control(); //initilises the cotrol class
  Serial.begin(9600); //sets port frequency
  //initilises all motors
  for (int i = 0; i < size(Bjy48); i++) Bjy48[i] = new BJY48(stepsPerRevBJY48, rolePerMinBJY48, pinsBJY48[i]);
  NEMA17Pos = new Nema17(pinsNEMA17Pos, dirNEMA17Pos, 2, MyControl, pinCsPos[0]);
  NEMA17Ali = new Nema17(pinsNEMA17Ali, dirNEMA17Ali, 1, MyControl, pinCsAli[0]);
  NEMA17Arr = new Nema17(pinsNEMA17Arr, dirNEMA17Arr, 2, MyControl, pinCsArr[0]);
  NEMA17Vac = new Nema17(pinsNEMA17Vac, dirNEMA17Vac, 1, MyControl, pinCsVac[0]);
  NEMA17Test = new myStepper(35, 39, 41, 200, 500, A7);
  //initilises valves and magnets
  ValveAlignment = new OnOff(pinValveAlignment);
  ValveWelding = new OnOff(pinValveWelding);
  ValveVacuum = new OnOff(pinValveVacuum);
  PumpVacuum = new OnOff(pinPumpVacuum);
  Magnets = new OnOff(pinMagnets);
  //initilises all switches
  for (int i = 0; i < size(CsPos); i++) CsPos[i] = new Contactswitch(pinCsPos[i]);
  for (int i = 0; i < size(CsAli); i++) CsAli[i] = new Contactswitch(pinCsAli[i]);
  for (int i = 0; i < size(CsArr); i++) CsArr[i] = new Contactswitch(pinCsArr[i]);
  for (int i = 0; i < size(CsVac); i++) CsVac[i] = new Contactswitch(pinCsVac[i]);
  for (int i = 0; i < size(PsVac); i++) PsVac[i] = new Contactswitch(pinPsVac[i]);
  pinMode(33, OUTPUT); //reset pin of motors needs to be high on v3 boards
  digitalWrite(33, HIGH);
}

void loop() {
  //bif (Serial.available()) Serial.println(Serial.read());
  
    //if (ValveVacuum->Status() && PsVac[0]->Status()) Serial.println("Alert Vacuum"); //checks weather vacuum is working if activated
    MyControl->Check(); //checks serial for new massages
    if (MyControl->BufferPos() > 0) {
    parseTask(MyControl->Buffer(1)); //pases and executes first task in line
    MyControl->GoOn();
    }
    //MyControl->Check(); //checks again before confim completion
    if (MyControl->BufferPos() == 0 && MyControl->Runs()) {
    Serial.println("complete");
    MyControl->Runs(false);

    }
  
}
