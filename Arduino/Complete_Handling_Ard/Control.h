/*
  Control.h - Libary for handling Multiple tasks on Arduino
  Created by Pascal Berger, November, 2019 at Fraunhofer IPA
*/

#ifndef Control_h
#define Control_h
class Control {
  private:
    String m_Buffer[100][4]; //all incoming massages are saved here;
    int m_BufferPos; //the current lenth of the buffer
    bool m_Runs; //task is running or not
    String m_Massage[4]; //cache for first massage
  public:
    inline Control() {
      m_BufferPos = 0;
      m_Runs = false;
    }
    inline bool Runs() {
      return m_Runs;
    }
    inline bool Runs(bool runs) {
      m_Runs = runs;
      return m_Runs;
    }
    inline String* Buffer(int bufferPos) { //returns the massage at the given buffer position
      return m_Buffer[bufferPos];
    }
    inline int BufferPos() {
      return m_BufferPos;
    }
    String* GoOn();
    bool Check();
};

bool Control::Check() { //checks for new massages and saves them in buffer and returns true when no new task needs to be done
  if (!Serial.available()) return true; //checks serial
  else {
    m_BufferPos++;
    for (int i = 0; i < 4; i++) m_Buffer[m_BufferPos][i] = Serial.readStringUntil('|'); //reads massage parts in buffer
    if (m_Buffer[m_BufferPos][2] == "stop") return false; //if codeword stop is in order returns false
    else {
      m_Runs = true;
      return true;
    }
  }
}
String* Control::GoOn() {//deletes the first task in the buffer and moves all tasks one up in line
  *m_Massage =  *m_Buffer[1];
  for (int i = 2; i <= m_BufferPos; i++) *m_Buffer[i - 1] = *m_Buffer[i];
  if (m_BufferPos > 0) m_BufferPos--;
  return m_Massage;
}

#endif
