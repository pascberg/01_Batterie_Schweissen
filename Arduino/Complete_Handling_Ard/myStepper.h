/*
  myStepper.h - Libary for handling Stepper
  Created by Pascal Berger, November, 2019 at Fraunhofer IPA
*/
#ifndef myStepper_h
#define myStepper_h


#include "Arduino.h"
#include <Stepper.h>
#include "Contactswitch.h"

class myStepper {
  private:
    Stepper* m_Motor;
    bool m_on;
    int m_pin[3];
    int m_StepsMade;
    Contactswitch* m_Cs;
  public:
    myStepper(int pinOn, int pinDir, int pinStep, int stepsPerRev, int rolePerMin, int pinContactswitch);
    inline int stepsMade() {
      return m_StepsMade;
    }
    inline int stepsMade(int stepsMade) { //function to track how much steps were made;
      m_StepsMade += stepsMade;
      return m_StepsMade;
    }
    bool steps(int steps);
    bool reset();
    inline bool onOff(bool on) {
      if (on) {
        digitalWrite(m_pin[0], HIGH);
        return m_on = true;
      }
      else {
        digitalWrite(m_pin[0], LOW);
        return m_on = false;
      }
    }
};
myStepper::myStepper(int pinOn, int pinDir, int pinStep, int stepsPerRev = 200, int rolePerMin = 100, int pinContactswitch = 0) {
  m_pin[0] = pinOn;
  m_pin[1] = pinDir;
  m_pin[2] = pinStep;

  pinMode(m_pin[0], OUTPUT);
  digitalWrite(m_pin[0], LOW);
  m_on = false;
  m_Motor = new Stepper(stepsPerRev, m_pin[1], m_pin[2]);
  m_Motor->setSpeed(rolePerMin);
  m_Cs = new Contactswitch(pinContactswitch);
}
bool myStepper::steps(int steps) { //motor makes steps and saves them
  m_Motor->step(steps);
  stepsMade(steps);
  return true;
}
bool myStepper::reset() {
  while (!m_Cs->Status())
    steps(-1);
  return true;
}
#endif
