import pickle
import numpy as np

def openConfig(filename):
    with open(filename, 'rb') as f:
        new_data = pickle.load(f)
        return new_data
def writeConfig(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

class Config:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.batpos = np.zeros((5,5,4))
        self.batAngleBefore = np.zeros((5,5))
        self.batAngleAfter = np.zeros((5,5))
        self.rotpos = np.zeros((5))
        self.Nema17Pos = list()
        self.Nema17Ali = list()
        self.Nema17Arr = list()
        self.Nema17Vac = list()
        self.initBatPos()
    def reset(self):
        self.batpos = np.zeros((5,5,4))
        self.rotpos = np.zeros((5))
    def initBatPos(self):
        width = 640
        height = 480
        edgeX = 0.2*width/2
        edgeY = 0.2*height/2
        absX = 0.1*width/4
        absY = 0.1*height/4
        dHeight = 0.7*width/5
        dWidth = 0.7*height/5
        for i in range(5):
            for j in range(5):
                self.batpos[i][j][0] = int(edgeX+j*dHeight+absX*j)
                self.batpos[i][j][1] = int(edgeY+i*dWidth+absY*i)
                self.batpos[i][j][2] = int(edgeX+(j+1)*dHeight+absX*j)
                self.batpos[i][j][3] = int(edgeY+(i+1)*dWidth+absY*i)
    def addPosition(self, listOfPositions, namePosition, positionInSteps):
        listOfPositions.append([namePosition, positionInSteps])
    def getPosition(self, listOfPositions, namePosition):
        data = None
        for position in listOfPositions:
            if position[0]==namePosition: data = position[1]
        if not data: data = "No Position"
        return data
    def delPosition(self, listOfPositions, namePosition):
        for i in range(len(listOfPositions)):
            if listOfPositions[i][0]== namePosition: del listOfPositions[i]
    def editPosition(self, position, newName, positionInSteps):
                position[0] = newName
                position[1] = positionInSteps
