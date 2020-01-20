/*
  BJY48.h - Libary for handling 28BJY48 stepper motors
  Created by Pascal Berger, November, 2019 at Fraunhofer IPA
*/
#ifndef BJY48_h
#define BJY48_h
#include <Stepper.h>

const float pi = 3.14159265359;
class BJY48 {
  private:
    Stepper* m_Motor;
    int m_RolePerMin;
    int m_StepsPerRev;
    int m_StepsMade;
  public:
    inline int stepsPerRev() {
      return m_StepsPerRev;
    }
    inline int stepsMade() {
      return m_StepsMade;
    }
    inline int stepsMade(int stepsMade) { //function to track how much steps were made;
      m_StepsMade += stepsMade;
      return m_StepsMade;
    }
    inline int stepsMade(bool reset) { //resets steps to zero
      if (reset) m_StepsMade = 0;
      return m_StepsMade;
    }
    inline Stepper* motor() {
      return m_Motor;
    }
    inline int rolePerMin() {
      return m_RolePerMin;
    }
    inline int rolePerMin(int rolePerMin) {
      if (abs(rolePerMin) <= 19) m_RolePerMin = abs(rolePerMin);
      else rolePerMin = 19;
      return m_RolePerMin;
    }
    BJY48(int stepsPerRev, int rolePerMin, int pins[4]);
    bool steps(int); //positiv clockwise
    bool moveRad(float angle);
};

BJY48::BJY48(int stepsPerRev, int rolePerMin, int pins[4]) //initilises BJY48
{
  m_RolePerMin = rolePerMin;
  m_StepsPerRev = stepsPerRev;
  m_StepsMade = 0;
  m_Motor = new Stepper(stepsPerRev, pins[1], pins[3], pins[0], pins[2]);
  m_Motor->setSpeed(rolePerMin);
}
bool BJY48::steps(int steps) { //motor makes steps and saves them
  m_Motor->step(steps);
  stepsMade(steps);
  return true;
}

bool BJY48::moveRad(float angle) { //moves the motor an angle in rad and saves the moved steps
  int steps = angle * (m_StepsPerRev / (2 * pi));
  m_Motor->step(steps);
  stepsMade(steps);
  return true;
}
#endif
