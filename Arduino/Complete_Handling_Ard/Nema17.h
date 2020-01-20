/*
  Nema17.h - Libary for handling an array of Nema17 stepper motors to run them simultaneously
  Created by Pascal Berger, November, 2019 at Fraunhofer IPA
*/
#include <AccelStepper.h>
#include "Contactswitch.h"
#include "Control.h"
#ifndef Nema17_h
#define Nema17_h

#include "Arduino.h"

class Nema17 {
  private:
    AccelStepper** m_MotorArray;
    AccelStepper* m_Motor;
    Control* m_Control;
    int m_MaxSpeed;
    int m_Accelaration;
    int m_Pins[3];
    bool *m_dir;
    Contactswitch *m_Cs;
    int m_Enable;
    int m_NumMotors;
    enum pinControl {Enable, Step, Direction};
  public:
    Nema17(int pins[][3], bool dir[], int numMotors, Control *control, int csPin, int maxSpeed, int accelaration);
    bool moveTo(int steps);
    bool moveSteps(int steps);
    bool reset();
    inline int Speed(int maxspeed) {
      m_MaxSpeed = maxspeed;
      return m_MaxSpeed;
    }
    inline int Speed() {
      return m_MaxSpeed;
    }
    inline int currentPosition(int motorNo = 0) { //returns the steps the motor made
      return m_MotorArray[motorNo]->currentPosition();
    }
};
Nema17::Nema17(int pins[][3], bool dir[], int numMotors, Control* control, int csPin = 0, int maxSpeed = 400, int accelaration = 10000) { //initilises multiple NEMA 17
  m_NumMotors = numMotors;
  m_MaxSpeed = maxSpeed;
  m_Accelaration = accelaration;
  m_MotorArray = new AccelStepper*[numMotors];
  m_Cs = new Contactswitch(csPin); //switch for endstop
  m_dir = dir;
  m_Control = control;
  m_Enable = pins[0][Enable];
  pinMode(m_Enable, OUTPUT);
  //pinMode(35, OUTPUT);
  for (int i = 0; i < numMotors; i++) {
    m_MotorArray[i] = new AccelStepper(1, pins[i][1], pins[i][2]);
    m_MotorArray[i]->setMaxSpeed(m_MaxSpeed);
    m_MotorArray[i]->setAcceleration(m_Accelaration);
  }
}
bool Nema17::moveTo(int steps) { //moves all motors to given steps
  digitalWrite(m_Enable, HIGH); //turns the motors on
  for (int i = 0; i < m_NumMotors; i++) { //sets all motors to given steps
    if (!m_dir[i]) m_MotorArray[i]->moveTo(-steps);
    else m_MotorArray[i]->moveTo(steps);
  }
  while (m_MotorArray[0]->currentPosition() != m_MotorArray[0]->targetPosition() && m_Control->Check()) {//moves the motors until they reacherd their destination or Check returns false
    for (int i = 0; i < m_NumMotors; i++) m_MotorArray[i]->run();
  }
  digitalWrite(m_Enable, LOW); //turns motors off
  return true;
}
bool Nema17::moveSteps(int steps) { //moves all motors a delta steps from their current position, almost same as moveTo
  digitalWrite(m_Enable, HIGH);
  for (int i = 0; i < m_NumMotors; i++) {
    if (!m_dir[i]) m_MotorArray[i]->move(-steps);
    else m_MotorArray[i]->move(steps);
  }
  while (m_MotorArray[0]->currentPosition() != m_MotorArray[0]->targetPosition() && m_Control->Check()) {
    for (int i = 0; i < m_NumMotors; i++) m_MotorArray[i]->run();
  }
  digitalWrite(m_Enable, LOW);
  return true;
}
bool Nema17::reset() { //moves all motors backwards until the endstop is reached, after that sets made steps to zero
  digitalWrite(m_Enable, HIGH);
  for (int i = 0; i < m_NumMotors; i++) {
    if (!m_dir[i]) m_MotorArray[i]->setSpeed(m_MaxSpeed);
    else m_MotorArray[i]->setSpeed(-m_MaxSpeed);
  }
  while (m_Control->Check()) {
    for (int i = 0; i < m_NumMotors; i++) m_MotorArray[i]->runSpeed();
    if (m_Cs->Status()) break;
  }
  for (int i = 0; i < m_NumMotors; i++) {
    m_MotorArray[i]->stop();
    m_MotorArray[i]->setCurrentPosition(0);
    digitalWrite(m_Enable, LOW);
    return true;
  }
  return false;
}
#endif