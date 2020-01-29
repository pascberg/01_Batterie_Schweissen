import threading
import time

import serial


# noinspection PyBroadException
class Arduino(threading.Thread):
    def __init__(self, gui, port='COM5', name="Arduino"):
        threading.Thread.__init__(self)
        self.gui = gui
        self.port = port
        self.name = name
        self.currentTask = 0
        self.connected = False
        self.runs = False
        self.gotMassage = False
        self.var = list()
        self.var.append("Started")
        try:
            self.Arduino = serial.Serial(self.port, 9600)
            # time.sleep(2) #wait for 2 Seconds until connection is established
            self.connected = True
        except:
            pass

    def run(self):
        self.runs = True
        if not self.connected:
            return
        while self.runs:
            self.readFromArduino()

    def readFromArduino(self):
        if self.Arduino.in_waiting:
            self.var.append(str(repr(self.Arduino.readline())[2:-5]))
            try:
                self.gui.FrameLeft.writeToInfo(self.name + " " + str(self.var[-1]))
            except:
                print(self.name + " " + str(self.var[-1]))
            time.sleep(0.1)
            return True
        else:
            time.sleep(0.1)
            return False

    def sendToArduino(self, task, wait=False):
        # task = ["Typ","Name","Order", "Data"]
        # try:
        massage = task[0] + '|' + task[1] + '|' + task[2] + '|' + task[3] + '|'
        self.Arduino.write(bytes(massage.encode("ascii")))
        # return massage
        while wait:
            if self.readFromArduino():
                if self.finishedArduino():
                    break
        # except:
        # print("Error: sendToArduino")
        # return False

    def finishedArduino(self):
        s = "complete"
        if self.var:
            if s in self.var[-1]:
                return True
        else:
            return False
