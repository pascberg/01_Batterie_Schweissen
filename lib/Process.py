import threading
import time

from gpiozero import Button

import lib.Functions as Func


class Process(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui
        self.currentTask = 0
        self.runs = False
        self.paused = False
        self.tasks = list()
        self.initTasks()

    def run(self):
        self.runs = True
        while self.runs:
            while not self.paused and self.runs:
                if self.currentTask < len(self.tasks):
                    self.tasks[self.currentTask][0](*self.tasks[self.currentTask][1])
                    time.sleep(2)
                    self.currentTask += 1
                if self.currentTask == len(self.tasks):
                    self.runs = False
                    self.gui.FrameLeft.writeToInfo("Process over")
        return

    def initTasks(self):
        config = self.gui.config
        # for i in range(2): #for testing purposes
        #    self.tasks.append([self.testTask, [i, 2]])
        # Reset Part
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["OnOff", "Pump", "set", "On"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "setSpeed", "400"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["Motor", "Nema17Ali", "reset", "None"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["Motor", "Nema17Pos", "reset", "None"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "reset", "None"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "PistonPos", "set", "Off"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "PistonAli", "set", "Off"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "Vacuum", "set", "Off"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "Magnets", "set", "Off"]]])
        # self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor","Nema17Vac",
        # "moveTo", str(config.getPosition(config.Nema17Vac, "Welding"))]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "moveTo", str(
            config.getPosition(config.Nema17Arr, "Spin"))]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Vac", "reset", "None"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Vac", "moveTo", str(
            config.getPosition(config.Nema17Vac, "Welding"))]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "reset", "None"]]])
        """
        # Angle acquisition
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["Motor", "Nema17Pos", "moveTo", str(
            config.getPosition(config.Nema17Pos, "Alignment"))]]])
        self.tasks.append([self.getAngles, [config.batAngleBefore]])
        # Alignment of batteries
        for i in range(1, 6):
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["Motor", "Nema17Ali", "moveTo", str(
                config.getPosition(config.Nema17Ali, "Ali " + str(i)))]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "PistonAli", "set", "On"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["", "", "wait", "1000"]]])
            for j in range(1, 6):
                self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["Motor", "48BJY28 " + str(j), "moveRad",
                                                                                str(config.batAngleBefore[i - 1][
                                                                                        j - 1])]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "Magnets", "set", "On"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "PistonAli", "set", "Off"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["", "", "wait", "1000"]]])
            for j in range(1, 6):
                self.tasks.append(
                    [self.gui.taskToArduino, [self.gui.Arduino1, ["Motor", "48BJY28 " + str(j), "reset", "None"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "Magnets", "set", "Off"]]])
        # Welding
        """
        for i in range(1, 6):
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["Motor", "Nema17Pos", "moveTo", str(
                config.getPosition(config.Nema17Pos, "Welding " + str(i)))]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "moveTo", str(
                config.getPosition(config.Nema17Arr, "Spin"))]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Vac", "moveTo", str(
                config.getPosition(config.Nema17Vac, "Arrester"))]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "moveTo", str(
                config.getPosition(config.Nema17Arr, "Welding"))]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["OnOff", "Vacuum", "set", "On"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "setSpeed", "50"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "moveTo", str(
                config.getPosition(config.Nema17Arr, "SpinSlow"))]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["", "", "wait", "1000"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "setSpeed", "400"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["", "", "wait", "1000"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Vac", "reset", "None"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Vac", "moveTo", str(
                config.getPosition(config.Nema17Vac, "Welding"))]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["Motor", "Nema17Arr", "reset", "None"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "PistonPos", "set", "On"]]])
            # !!!Welding!!!
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["", "", "wait", "10000"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["OnOff", "Vacuum", "set", "Off"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["OnOff", "PistonPos", "set", "Off"]]])
            self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["", "", "wait", "1000"]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino1, ["Motor", "Nema17Pos", "moveTo", str(
            config.getPosition(config.Nema17Pos, "Alignment"))]]])
        self.tasks.append([self.gui.taskToArduino, [self.gui.Arduino2, ["OnOff", "Pump", "set", "Off"]]])

        # Restart startProcessAir
        self.tasks.append([self.gui.FrameLeft.startAirControl, []])

    def testTask(self, i, j):
        self.gui.FrameLeft.writeToInfo("Task " + str(i * j))

    # noinspection PyAttributeOutsideInit
    def getAngles(self, batAngles):
        self.vcap = Func.openVideoCapture()
        success, img = self.vcap.read()
        Func.anglesBatteries(img, self.gui.config.batpos, batAngles)
        Func.closeVideoCapture(self.vcap)


class startProcessAir(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui
        self.runs = False
        self.pin = Button(17)

    def run(self):
        self.runs = True
        while self.runs:
            if self.pin.is_pressed:
                self.gui.frameLeft.processControl(1)
                break
                # button.when_pressed = self.gui.frameLeft.processControl(1)
            time.sleep(0.1)
