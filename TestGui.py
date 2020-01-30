#!/usr/bin/env python
# file for the complete user interface to control the handling of the batteries in the laser cell
import platform
import time
import tkinter as tk
from tkinter import ttk

import cv2

import lib.Arduino as Ard
import lib.Config as Conf
import lib.Dialog as Dlg
import lib.Functions as Func
import lib.LogFile as Log
import lib.Process as Proc

makeLogFile = False  # bool to turn logfiles on or off


# noinspection PyBroadException,PyUnusedLocal
class ProcessGui:  # main class where all instances are combined
    def __init__(self):
        self.window = tk.Tk()  # initialises main window
        self.window.title("GUI")
        self.window.resizable(0, 0)
        self.window.columnconfigure(0, weight=1)
        self.FrameLeft = frameLeft(self)
        self.FrameRight = frameRight(self)
        self.FrameLeft.frame.grid(row=0, column=0, sticky="nsw")  # initialises info frame
        self.FrameRight.frame.grid(row=0, column=1, sticky="nsew")  # initialises control frame
        self.log = None
        self.Process = list()  # list for handling threads
        self.startProcessAir = list()  # list for the pneumatic controlled threads
        if makeLogFile:
            self.log = Log.LogFile('Test')
        if platform.system() == "Windows":  # sets window to appropriate size for os and initialises Arduinos to their
            # compatible ports
            self.Arduino1 = Ard.Arduino(self, name="Arduino 1", port='COM7')
            self.Arduino2 = Ard.Arduino(self, name="Arduino 2", port='COM6')
            self.window.geometry("800x480")
        else:
            self.Arduino1 = Ard.Arduino(self, name="Arduino 1", port='/dev/ttyACM0')
            self.Arduino2 = Ard.Arduino(self, name="Arduino 2", port='/dev/ttyACM1')
            self.window.attributes('-fullscreen', True)
            self.window.geometry("800x480")
            self.FrameLeft.startAirControl(1)
        try:
            self.config = Conf.openConfig('GUI.config')  # try to load existing config, else makes new
        except:
            self.config = Conf.Config('GUI.config')
        self.window.bind("<ButtonRelease-1>", self.getNumber)

    def __enter__(self):
        print("Started")
        self.FrameLeft.writeToInfo("Started")
        self.Arduino1.start()  # starts threads to get all massages from Arduinos
        self.Arduino2.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Conf.writeConfig(self.config.filename, self.config)  # saves all data to save in config file
        for i in self.Process:
            i.runs = False  # gives all threads in process the stop signal
            if i.is_alive():
                i.join()
        for i in self.startProcessAir:
            i.runs = False  # gives all threads in process the stop signal
            if i.is_alive():
                i.join()
        self.sendToArduino(self.Arduino1, ["", "", "stop", ""])  # sends stop signal to arduinos
        self.sendToArduino(self.Arduino2, ["", "", "stop", ""])
        self.Arduino1.runs = False  # sends stop signal to arduino thread and waits for them to end
        self.Arduino1.join()
        self.Arduino2.runs = False
        self.Arduino2.join()
        print("Closed")

    @staticmethod
    def clearFrame(frame):  # kills all objects inside of frame
        a = frame.winfo_children()
        for item in a:
            item.destroy()

    def sendToArduino(self, Arduino, message):  # sends a massage to arduino
        # message = ["Typ","Name","Order", "Data"]
        if Arduino.connected:
            Arduino.sendToArduino(message)
        else:
            self.FrameLeft.writeToInfo(str(Arduino.name) + " not connected")

    def taskToArduino(self, Arduino, message):  # sends a massage to arduino, but waits until arduino is finished
        # message = ["Typ","Name","Order", "Data"]
        if Arduino.connected:
            if self.log:
                self.log.writeToLogFile(str(message))
            Arduino.sendToArduino(message)
            s = "complete"
            while True:
                if s in Arduino.var[-1]:
                    break
                time.sleep(0.1)
        else:
            self.FrameLeft.writeToInfo(str(Arduino.name) + " not connected")

    # noinspection PyTypeChecker
    def getNumber(self, event):  # short function to open number dialog any time a entry field is clicked
        focus = self.window.focus_get()
        if type(focus) == tk.Entry:
            value = [focus.get()]
            if value[0] == '0':
                value[0] = None
            Dlg.dialogNumber(self, title="Number Dialog", value=value)
            if value[0]:
                focus.delete(0, tk.END)
                focus.insert(tk.END, int(value[0]))


class frameRight:  # frame for various controls
    def __init__(self, gui):  # initialises empty frame
        self.gui = gui
        self.frame = tk.Frame(self.gui.window)


# noinspection PyUnusedLocal
class frameLeft:  # frame for process control, massage box and control tree
    def __init__(self, gui):  # initialises frame
        self.gui = gui
        self.frame = tk.Frame(self.gui.window)
        # Info panel
        self.info = tk.Text(self.frame, width=37, height=11)
        self.scrollInfo = tk.Scrollbar(self.frame)
        self.scrollInfo.config(command=self.info.yview)
        self.info.config(yscrollcommand=self.scrollInfo.set, state=tk.DISABLED)
        # Buttons
        self.buttonStart = tk.Button(self.frame, text="Start", command=lambda: self.processControl(1))
        self.buttonPause = tk.Button(self.frame, text="Pause", command=lambda: self.processControl(0))
        self.buttonStop = tk.Button(self.frame, text="Stop", command=lambda: self.processControl(-1))
        self.buttonExit = tk.Button(self.frame, text="Beenden", command=self.gui.window.quit)
        # Tree
        self.tree = ttk.Treeview(self.frame)
        self.scrollTree = tk.Scrollbar(self.frame)
        self.scrollTree.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=self.scrollTree.set)
        # Treeview
        self.Clear = self.tree.insert('', 'end', text='Clear')
        self.ImageProcess = self.tree.insert('', 'end', text='Image Process')
        self.CameraAlignment = self.tree.insert(self.ImageProcess, 'end', text='Camera')
        self.BatteryAlignment = list()
        for i in range(5):
            self.BatteryAlignment.append(
                self.tree.insert(self.ImageProcess, 'end', text='Batteries Column ' + str(i + 1)))
        self.Alignment = self.tree.insert('', 'end', text='Alignment')
        self.Positioning = self.tree.insert('', 'end', text='Positioning')
        self.Arrester = self.tree.insert('', 'end', text='Arrester')
        self.Test = self.tree.insert('', 'end', text='Test')
        self.tree.bind("<ButtonRelease-1>", self.treeClicked)
        # Grid
        self.buttonStart.grid(row=0, column=0, sticky="nsew", pady=3, padx=3)
        self.buttonPause.grid(row=1, column=0, sticky="nsew", pady=3, padx=3)
        self.buttonStop.grid(row=2, column=0, sticky="nsew", pady=3, padx=3)
        self.buttonExit.grid(row=3, column=0, sticky="nsew", pady=3, padx=3)
        self.tree.grid(row=0, column=1, columnspan=1, rowspan=4, sticky="nsew", pady=10)
        self.scrollTree.grid(row=0, column=4, rowspan=4, sticky="nse", pady=10)
        self.info.grid(row=4, column=0, columnspan=2, rowspan=2, sticky="nsew")
        self.scrollInfo.grid(row=4, column=4, rowspan=2, sticky="nse")

    def writeToInfo(self, s):  # writes a massage to the textbox and logfile if present
        try:
            self.info.config(state=tk.NORMAL)  # enables and disables writing so only functions can write massages
            self.info.insert(tk.END, str(s) + '\n')
            self.info.config(state=tk.DISABLED)
            self.info.see(tk.END)
        except:
            print(s)
        if self.gui.log:
            self.gui.log.writeToLogFile(str(s))

    def treeClicked(self, event):  # function to determine which tree element was clicked and init their class
        if self.tree.focus() == self.CameraAlignment:
            camera(self)
        for i in self.BatteryAlignment:
            if self.tree.focus() == i:
                batteryAlignment(self, self.BatteryAlignment.index(i))
        if self.tree.focus() == self.Clear:
            self.gui.clearFrame(self.gui.FrameRight.frame)
        if self.tree.focus() == self.Alignment:
            alignment(self)
        if self.tree.focus() == self.Positioning:
            positioning(self)
        if self.tree.focus() == self.Arrester:
            arrester(self)
        if self.tree.focus() == self.Test:
            test(self.gui)

    def processControl(self, control):  # controls the process and its threads, contorl is just an int
        if not self.gui.Process:
            self.gui.Process.append(Proc.Process(self.gui))
        else:
            if not self.gui.Process[-1].isAlive():
                self.gui.Process.pop(-1)
                self.gui.Process.append(Proc.Process(self.gui))
        if control == 1:
            if self.gui.Process[-1].runs:
                if self.gui.Process[-1].paused:
                    self.gui.Process[-1].paused = False
                else:
                    self.writeToInfo("Process is running")
            else:
                self.gui.Process[-1].start()
        if control == 0:
            if self.gui.Process[-1].paused:
                self.gui.Process[-1].paused = False
            else:
                self.gui.Process[-1].paused = True
        if control == -1:
            self.gui.sendToArduino(self.gui.Arduino1, ["", "", "stop", ""])
            self.gui.sendToArduino(self.gui.Arduino2, ["", "", "stop", ""])
            if self.gui.Process[-1].runs:
                self.gui.Process[-1].runs = False
            else:
                self.writeToInfo("Process has not been started")

    def startAirControl(self, control):
        if control == 1:
            if not self.gui.startProcessAir:
                self.gui.startProcessAir.append(Proc.startProcessAir(self.gui))
            else:
                if not self.gui.startProcessAir[-1].isAlive():
                    self.gui.startProcessAir.pop(-1)
                    self.gui.startProcessAir.append(Proc.Process(self.gui))
            self.gui.startProcessAir[-1].start()
        if control == 0:
            self.gui.startProcessAir[-1].run = False


# noinspection PyBroadException,PyUnusedLocal
class stream:  # class for streaming video from ip camera
    # the standard camera config is saved in Functions.py as default, but can be changed here if needed
    def __init__(self, frame, func=None,
                 arg=None):  # initialises the stream and video size, frames and video capture, func can be used to
        # alter stream
        self.frame = frame
        self.func = func
        self.arg = arg
        self.vcap = None
        self.vWidth = None
        self.vHeight = None
        self.vFPS = None
        self.vFrame = tk.Frame(self.frame.frame.gui.FrameRight.frame, width=400)
        self.stream = tk.Label(self.vFrame)
        self.stream.grid(row=0, column=0)
        try:
            self.vcap = Func.openVideoCapture()
            self.vWidth = self.vcap.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.vHeight = self.vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.vFPS = self.vcap.get(cv2.CAP_PROP_FPS)
            self.stream.after(int(1000 / self.vFPS / 2), lambda: self.streamFrame(self.stream, self.vcap))
        except:
            self.frame.frame.writeToInfo("Camera not connected")

    def __enter__(self):  # only needed because exit is needed
        return self

    def __exit__(self):  # only needed to close video capture
        Func.closeVideoCapture(self.vcap)

    def streamFrame(self, label, vcap):  # streams the video and refreshes matching the fps
        if self.vcap:
            success, img = vcap.read()
            try:
                self.func(img, self.arg)
            except:
                pass
            wHeight = self.frame.frame.gui.window.winfo_height()
            wWidth = self.frame.frame.gui.window.winfo_width()
            tempWidth = int(wWidth / self.vWidth * 0.5 * self.vWidth)
            tempHeight = int(wWidth / self.vWidth * 0.5 * self.vHeight)
            img = cv2.resize(img, (tempWidth, tempHeight))
            label.after(int(1000 / self.vFPS / 2), lambda: self.streamFrame(label, vcap))
            photo = Func.cv2ToTk(img)
            label.config(image=photo)
            label.image = photo

    def safeScreenshot(self):  # safes a screenshot, but without function
        success, img = self.vcap.read()
        filename = "screenshot " + Func.getTimeStamp("%d-%b-%Y %H-%M-%S") + ".jpg"
        cv2.imwrite(filename, img)
        self.frame.frame.writeToInfo("Screenshot saved")


class motorControl:  # class to hold all controls for Nema17 or 28BYJ48
    def __init__(self, frame, Arduino, motorName):  # inits control buttons and belonging arduino
        self.frame = frame
        self.gui = self.frame.frame.gui
        self.motorName = motorName
        self.Arduino = Arduino
        self.mFrame = tk.Frame(self.frame.frame.gui.FrameRight.frame)
        self.labelName = tk.Label(self.mFrame, text=self.motorName)
        self.entrySteps = tk.Entry(self.mFrame, justify=tk.CENTER, width=5)
        self.entrySteps.insert(tk.END, 0)
        self.buttonMoveSteps = tk.Button(self.mFrame, text="Move",
                                         command=lambda: self.setSteps(int(self.entrySteps.get())))
        self.buttonReset = tk.Button(self.mFrame, text="Reset", command=lambda: self.setSteps(False))
        self.buttonConfig = tk.Button(self.mFrame, text="Config", command=lambda: self.motorConfig())
        self.labelName.grid(row=0, column=1, padx=3, pady=2, sticky="nsw")
        self.entrySteps.grid(row=0, column=2, padx=3, pady=2, sticky="nsw")
        self.buttonMoveSteps.grid(row=0, column=3, padx=3, pady=2, sticky="nsw")
        self.buttonReset.grid(row=0, column=4, padx=3, pady=2, sticky="nsw")
        self.buttonConfig.grid(row=0, column=5, padx=3, pady=2, sticky="nsw")

    def motorConfig(self):  # function to open corresponding config
        if self.motorName == "Nema17Ali":
            Dlg.motorConfig(self.gui, title="MotorConfig", listOfPositions=self.gui.config.Nema17Ali,
                            motorName=self.motorName, motor=self)
        if self.motorName == "Nema17Pos":
            Dlg.motorConfig(self.gui, title="MotorConfig", listOfPositions=self.gui.config.Nema17Pos,
                            motorName=self.motorName, motor=self)
        if self.motorName == "Nema17Arr":
            Dlg.motorConfig(self.gui, title="MotorConfig", listOfPositions=self.gui.config.Nema17Arr,
                            motorName=self.motorName, motor=self)
        if self.motorName == "Nema17Vac":
            Dlg.motorConfig(self.gui, title="MotorConfig", listOfPositions=self.gui.config.Nema17Vac,
                            motorName=self.motorName, motor=self)

    def setSteps(self, steps):
        if not steps:
            self.gui.sendToArduino(self.Arduino, ["Motor", self.motorName, "reset", "None"])
        else:
            self.gui.sendToArduino(self.Arduino, ["Motor", self.motorName, "moveSteps", str(int(steps))])


class onOffControl:  # class to hold all controls for OnOff
    def __init__(self, frame, Arduino, name):  # inits control buttons and belonging arduino
        self.frame = frame
        self.name = name
        self.Arduino = Arduino
        self.mFrame = tk.Frame(self.frame.frame.gui.FrameRight.frame)
        self.labelName = tk.Label(self.mFrame, text=self.name)
        self.buttons = list()
        self.buttons.append(tk.Button(self.mFrame, text="On", command=lambda: self.setOnOff("On")))
        self.buttons.append(tk.Button(self.mFrame, text="Off", command=lambda: self.setOnOff("Off")))
        self.canvasStatus = tk.Canvas(self.mFrame, width=20, height=20)
        self.canvasStatus.create_rectangle(0, 0, 300, 300, fill="green")
        self.labelName.grid(row=0, column=0, columnspan=1, sticky="nsw")
        for i in range(len(self.buttons)):
            self.buttons[i].config(height=1, width=5)
            self.buttons[i].grid(row=0, column=i + 1, padx=3, pady=2, sticky="nsew")
        self.canvasStatus.grid(row=0, column=5, sticky="nse", columnspan=1, rowspan=1, padx=3, pady=2)

    def setOnOff(self, onOff):  # sends signal to arduino to turn it on or off
        self.frame.frame.gui.sendToArduino(self.Arduino, ["OnOff", self.name, "set", str(onOff)])


class camera:  # class just for handling a camera stream with only option to take screenshot
    def __init__(self, frame):  # inits stream and button
        self.frame = frame
        self.frame.gui.clearFrame(self.frame.gui.FrameRight.frame)
        self.buttonSafeScreenshot = tk.Button(self.frame.gui.FrameRight.frame, text="Save screenshot",
                                              command=lambda: self.stream.safeScreenshot())
        self.buttonSafeScreenshot.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)
        self.stream = stream(self)
        self.stream.vFrame.grid(row=0, column=0, columnspan=6, sticky="nsew")


class batteryAlignment:  # class for ui to change positions from battery positions
    def __init__(self, frame, row):  # initialises all fields and loads data from config
        self.frame = frame
        self.row = row
        self.frame.gui.clearFrame(self.frame.gui.FrameRight.frame)
        self.stream = stream(self, Func.anglesBatteries, self.frame.gui.config.batpos)
        self.stream.vFrame.grid(row=0, column=0, columnspan=6, sticky="nsew")
        self.labelPos = list()
        self.labelPos.append(
            tk.Label(self.frame.gui.FrameRight.frame, text="TopLeft X").grid(row=1, column=0, sticky="nsw"))
        self.labelPos.append(
            tk.Label(self.frame.gui.FrameRight.frame, text="TopLeft Y").grid(row=2, column=0, sticky="nsw"))
        self.labelPos.append(
            tk.Label(self.frame.gui.FrameRight.frame, text="BottomRight X").grid(row=3, column=0, sticky="nsw"))
        self.labelPos.append(
            tk.Label(self.frame.gui.FrameRight.frame, text="BottomRight Y").grid(row=4, column=0, sticky="nsw"))
        self.batpos = list()
        for i in range(5):
            for j in range(4):
                self.batpos.append(tk.Entry(self.frame.gui.FrameRight.frame,
                                            justify=tk.CENTER,
                                            width=5))
                self.batpos[4 * i + j].grid(row=j + 1, column=i + 1, sticky="nsw", pady=2, padx=1)
                self.batpos[4 * i + j].insert(tk.END, str(int(self.frame.gui.config.batpos[row][i][j])))
        self.buttonRefresh = tk.Button(self.frame.gui.FrameRight.frame, text="Refresh",
                                       command=lambda: self.refresh()).grid(row=5, column=0)
        self.frame.gui.window.bind('<Return>', self.enter)

    def enter(self):  # refreshes all values when initialised
        self.refresh()

    def refresh(self):  # refreshes all values
        for i in range(5):
            for j in range(4):
                self.frame.gui.config.batpos[self.row][i][j] = int(self.batpos[4 * i + j].get())
        self.frame.writeToInfo("Battery positions updated")


class alignment:  # class which holds all controls for the alignment part
    def __init__(self, frame):  # initialises different control classes
        self.frame = frame
        self.frame.gui.clearFrame(self.frame.gui.FrameRight.frame)
        self.Nema17 = motorControl(self, self.frame.gui.Arduino1, "Nema17Ali")
        self.Nema17.mFrame.grid(row=0, column=0, sticky="nsew")
        self.BJY28 = list()
        for i in range(5):
            self.BJY28.append(motorControl(self, self.frame.gui.Arduino1, "48BJY28 " + str(1 + i)))
            self.BJY28[i].mFrame.grid(row=i + 1, column=0, sticky="nsew")
        self.Piston = onOffControl(self, self.frame.gui.Arduino1, "PistonAli")
        self.Piston.mFrame.grid(row=7, column=0, sticky="nsew")
        self.Magnets = onOffControl(self, self.frame.gui.Arduino1, "Magnets")
        self.Magnets.mFrame.grid(row=8, column=0, sticky="nsew")


class positioning:  # class which holds all controls for the positioning part
    def __init__(self, frame):
        self.frame = frame
        self.frame.gui.clearFrame(self.frame.gui.FrameRight.frame)
        self.Nema17 = motorControl(self, self.frame.gui.Arduino1, "Nema17Pos")
        self.Nema17.mFrame.grid(row=0, column=0, sticky="nsew")
        self.Piston = onOffControl(self, self.frame.gui.Arduino1, "PistonPos")
        self.Piston.mFrame.grid(row=1, column=0, sticky="nsew")


class arrester:  # class which holds all controls for the arrester part
    def __init__(self, frame):
        self.frame = frame
        self.frame.gui.clearFrame(self.frame.gui.FrameRight.frame)
        self.Nema17 = motorControl(self, self.frame.gui.Arduino2, "Nema17Arr")
        self.Nema17.mFrame.grid(row=0, column=0, sticky="nsew")
        self.Nema17 = motorControl(self, self.frame.gui.Arduino2, "Nema17Vac")
        self.Nema17.mFrame.grid(row=1, column=0, sticky="nsew")
        self.Vacuum = onOffControl(self, self.frame.gui.Arduino2, "Vacuum")
        self.Vacuum.mFrame.grid(row=2, column=0, sticky="nsew")
        self.Pump = onOffControl(self, self.frame.gui.Arduino2, "Pump")
        self.Pump.mFrame.grid(row=3, column=0, sticky="nsew")
        self.BigPump = onOffControl(self, self.frame.gui.Arduino2, "BigPump")
        self.BigPump.mFrame.grid(row=4, column=0, sticky="nsew")


class test:  # just for testing stuff
    def __init__(self, gui):
        self.gui = gui
        print("Test")
        self.frame = gui.FrameRight
        self.gui.clearFrame(self.gui.FrameRight.frame)
        self.Nema17 = motorControl(self, self.frame.gui.Arduino2, "Nema17Arr")
        self.Nema17.mFrame.grid(row=0, column=0, sticky="nsew")
        self.buttonTest = tk.Button(self.gui.FrameRight.frame, text="Test", command=lambda: self.setSteps())
        self.buttonTest.grid(row=1, column=0, padx=3, pady=2, sticky="nsw")

    def setSteps(self):
        self.gui.taskToArduino(self.gui.Arduino2, ["Test1", "Test2", "wait", "2000"])


with ProcessGui() as root:  # loop for main applications
    root.window.mainloop()
