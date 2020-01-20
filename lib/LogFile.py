import lib.Functions as Func

class LogFile:
    def __init__(self, name = 'log'):
        self.name = 'log'
        self.logFileName = 'log '+ Func.getTimeStamp("%d-%b-%Y %H-%M-%S")+ ".log"
        self.logFile= open(self.logFileName,"w+")
        self.logFile.write(Func.getTimeStamp()+" " + "Start" + "\n")
        self.logFile.close()
    def writeToLogFile(self, content):
        self.logFile = open(self.logFileName,"a")
        self.logFile.write(Func.getTimeStamp()+" " + content + '\n')
        self.logFile.close()
