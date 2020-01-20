/*
  OnOff.h - Libary for handling OnOff devices
  Created by Pascal Berger, November, 2019 at Fraunhofer IPA
*/
#ifndef OnOff_h
#define OnOff_h

#include "Arduino.h"
class OnOff {
  private:
    bool m_on;
    int m_pin;
  public:
    inline OnOff(int pin) {
      m_pin = pin;
      pinMode(m_pin, OUTPUT);
    }
    bool on();
    bool off();
    inline bool Status() {
      return m_on;
    }
};
bool OnOff::on() {
  digitalWrite(m_pin, HIGH);
  m_on = true;
  return m_on;
}
bool OnOff::off()
{
  digitalWrite(m_pin, LOW);
  m_on = false;
  return m_on;
}

#endif
