import serial
import threading
import time


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
            if self.Arduino.in_waiting:
                self.var.append(str(repr(self.Arduino.readline())[2:-5]))
                self.gui.FrameLeft.writeToInfo(self.name + " " + str(self.var[-1]))
            time.sleep(0.1)

    def sendToArduino(self, task, wait=False):
        # task = ["Typ","Name","Order", "Data"]
        # try:
        massage = task[0] + '|' + task[1] + '|' + task[2] + '|' + task[3] + '|'
        self.Arduino.write(bytes(massage.encode("ascii")))
        # return massage
        while wait:
            if self.finishedArduino():
                break
            time.sleep(0.1)
        # except:
        # print("Error: sendToArduino")
        # return False

    def finishedArduino(self):
        s = "complete"
        if self.var:
            if s in str(self.var[-1]):
                return True
        else:
            return False
