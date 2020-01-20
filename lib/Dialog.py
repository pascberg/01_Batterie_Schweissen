import tkinter as tk
from tkinter import ttk
import time
import os


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class Dialog(tk.Toplevel):

    def __init__(self, gui, **kwargs):
        self.gui = gui
        self.args = kwargs
        parent = self.gui.window
        tk.Toplevel.__init__(self, parent)
        self.resizable(0, 0)
        self.transient(parent)
        if 'title' in self.args:
            self.title(self.args.get('title'))
        self.result = None
        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    # construction hooks
    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = tk.Frame(self)
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.gui.window.focus_set()
        self.destroy()

    # command hooks
    def validate(self):
        return 1  # override

    def apply(self):
        pass


# noinspection PyAttributeOutsideInit,PyBroadException
class dialogNumber(Dialog):
    def body(self, master):
        self.textInput = tk.Text(master, width=10, height=1)
        self.value = None
        if 'value' in self.args:
            self.value = self.args.get('value')
            if self.value[0]:
                self.textInput.insert(tk.END, self.value[0])
        self.textInput.config(state=tk.DISABLED)
        self.buttons = list()
        self.buttons.append(tk.Button(master, text=" 0 ", command=lambda: self.numberPressed(0)))
        self.buttons.append(tk.Button(master, text=" 1 ", command=lambda: self.numberPressed(1)))
        self.buttons.append(tk.Button(master, text="2", command=lambda: self.numberPressed(2)))
        self.buttons.append(tk.Button(master, text="3", command=lambda: self.numberPressed(3)))
        self.buttons.append(tk.Button(master, text="4", command=lambda: self.numberPressed(4)))
        self.buttons.append(tk.Button(master, text="5", command=lambda: self.numberPressed(5)))
        self.buttons.append(tk.Button(master, text="6", command=lambda: self.numberPressed(6)))
        self.buttons.append(tk.Button(master, text="7", command=lambda: self.numberPressed(7)))
        self.buttons.append(tk.Button(master, text="8", command=lambda: self.numberPressed(8)))
        self.buttons.append(tk.Button(master, text="9", command=lambda: self.numberPressed(9)))
        self.buttons.append(tk.Button(master, text="Del", command=lambda: self.delLast()))
        self.buttons.append(tk.Button(master, text=".", command=lambda: self.numberPressed(".")))
        self.buttons.append(tk.Button(master, text="-", command=lambda: self.numberPressed("-")))
        self.textInput.grid(row=0, column=0, columnspan=3)
        self.buttons[1].grid(row=1, column=0, sticky="nsew", pady=1, padx=1)
        self.buttons[2].grid(row=1, column=1, sticky="nsew", pady=1, padx=1)
        self.buttons[3].grid(row=1, column=2, sticky="nsew", pady=1, padx=1)
        self.buttons[4].grid(row=2, column=0, sticky="nsew", pady=1, padx=1)
        self.buttons[5].grid(row=2, column=1, sticky="nsew", pady=1, padx=1)
        self.buttons[6].grid(row=2, column=2, sticky="nsew", pady=1, padx=1)
        self.buttons[7].grid(row=3, column=0, sticky="nsew", pady=1, padx=1)
        self.buttons[8].grid(row=3, column=1, sticky="nsew", pady=1, padx=1)
        self.buttons[9].grid(row=3, column=2, sticky="nsew", pady=1, padx=1)
        self.buttons[11].grid(row=4, column=0, sticky="nsew", pady=1, padx=1)
        self.buttons[0].grid(row=4, column=1, sticky="nsew", pady=1, padx=1)
        self.buttons[10].grid(row=4, column=2, sticky="nsew", pady=1, padx=1)
        self.buttons[12].grid(row=4, column=3, sticky="nsew", pady=1, padx=1)
        # return self.e1 # initial focus

    def numberPressed(self, value):
        self.textInput.config(state=tk.NORMAL)
        self.textInput.insert(tk.END, str(value))
        self.textInput.config(state=tk.DISABLED)

    def delLast(self):
        self.textInput.config(state=tk.NORMAL)
        temp = self.textInput.get("1.0", 'end-1c')[:-1]
        self.textInput.delete("1.0", tk.END)
        self.textInput.insert(tk.END, temp)
        self.textInput.config(state=tk.DISABLED)
        self.textInput.update()

    def apply(self):
        try:
            first = float(self.textInput.get("1.0", tk.END))
            # self.gui.FrameLeft.writeToInfo(first)
            self.value[0] = first
        except:
            self.gui.FrameLeft.writeToInfo("Bad Input")


# noinspection PyAttributeOutsideInit,PyBroadException,PyUnusedLocal
class motorConfig(Dialog):
    def body(self, master):
        self.motor = self.args.get('motor')
        if 'listOfPositions' in self.args:
            self.pos = self.args.get('listOfPositions')
        else:
            self.pos = list()
        self.frame = tk.Frame(master)
        self.frame.grid(row=0, column=0)
        self.frameBody(self.frame)

    def frameBody(self, master):
        self.master = master
        self.motor = self.args.get('motor')
        if 'listOfPositions' in self.args:
            self.pos = self.args.get('listOfPositions')
        else:
            self.pos = list()
        # Tree
        self.tree = ttk.Treeview(master, columns='Steps')
        self.scrollTree = tk.Scrollbar(master)
        self.scrollTree.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=self.scrollTree.set)

        for i in range(len(self.pos)):
            self.tree.insert("", "end", text=self.pos[i][0], values=(self.pos[i][1]))
        # self.tree.bind("<Double-Button-1>", self.editPosition)
        self.tree.grid(row=0, column=0, columnspan=1, rowspan=4, sticky="nsew", pady=10)
        self.scrollTree.grid(row=0, column=1, rowspan=4, sticky="nse", pady=10)
        self.buttonNew = tk.Button(master, text=" New ", command=lambda: self.newPosition())
        self.buttonConf = tk.Button(master, text="Edit", command=lambda: self.editPosition())
        self.buttonDel = tk.Button(master, text="Delete", command=lambda: self.delPosition())
        self.buttonMove = tk.Button(master, text="Move", command=lambda: self.movePosition())
        self.buttonNew.grid(row=0, column=2, rowspan=1, sticky="nsew", pady=2)
        self.buttonConf.grid(row=1, column=2, rowspan=1, sticky="nsew", pady=2)
        self.buttonDel.grid(row=2, column=2, rowspan=1, sticky="nsew", pady=2)
        self.buttonMove.grid(row=3, column=2, rowspan=1, sticky="nsew", pady=2)

    def mUpdate(self):
        self.frameBody(self.frame)

    def editPosition(self, event=None):
        index = self.tree.index(self.tree.focus())
        editPos(self.gui, position=self.pos[index])
        self.mUpdate()

    def newPosition(self):
        position = [None, 0]
        self.gui.taskToArduino(self.motor.Arduino, ["Motor", self.motor.motorName, "position", "None"])
        for i in range(3):
            self.after(50, self.update())
        try:
            position[1] = int(self.motor.Arduino.var[-2])
        except:
            pass
        editPos(self.gui, position=position)
        if position[0] and position[1]:
            self.pos.append(position)
        self.mUpdate()

    def delPosition(self):
        index = self.tree.index(self.tree.focus())
        self.gui.config.delPosition(self.pos, self.pos[index][0])
        self.mUpdate()

    def movePosition(self):
        index = self.tree.index(self.tree.focus())
        self.gui.sendToArduino(self.motor.Arduino, ["Motor", self.motor.motorName, "moveTo", str(self.pos[index][1])])
        # self.motor.Arduino.sendToArduino(["Motor", self.motor.motorName, "moveTo", self.pos[index][1]])
        self.mUpdate()

    def apply(self):
        pass


# noinspection PyAttributeOutsideInit,PyBroadException
class editPos(Dialog):
    def body(self, master):
        if 'position' in self.args:
            self.position = self.args.get('position')
        tk.Label(master, text="Name:").grid(row=0)
        tk.Label(master, text="Steps:").grid(row=1)

        self.entryName = tk.Entry(master)
        if self.position[0]:
            self.entryName.insert(tk.END, self.position[0])
        self.entryValue = tk.Entry(master)
        if self.position[1]:
            self.entryValue.insert(tk.END, self.position[1])

        self.entryName.grid(row=0, column=1)
        self.entryValue.grid(row=1, column=1)
        return self.entryName  # initial focus

    def apply(self):
        try:
            name = self.entryName.get()
            value = int(self.entryValue.get())
            self.gui.config.editPosition(self.position, name, value)
        except:
            self.gui.FrameLeft.writeToInfo("Bad input")
