/*
  ContactSwitch.h - Libary for handling contact switches and other digital inputs
  Created by Pascal Berger, November, 2019 at Fraunhofer IPA
*/
#ifndef Contactswitch_h
#define Contactswitch_h

#include "Arduino.h"

class Contactswitch {
  private:
    int m_Pin;
    int m_Value;
  public:
    inline Contactswitch(int pin) {
      m_Pin = pin;
      pinMode(m_Pin, INPUT);
    }
    inline Contactswitch(Contactswitch &a) {
      m_Pin = a.m_Pin;
      pinMode(m_Pin, INPUT);
    }
    inline int Value() {
      m_Value = digitalRead(m_Pin);
      return m_Value;
    }
    bool Status();
};
bool Contactswitch::Status()
{
  if (Value() == 1) return true;
  else return false;
}

#endif
