import numpy as np
import cv2
import PIL.Image
import PIL.ImageTk
from datetime import datetime


# noinspection PyBroadException
def openVideoCapture(user="admin", password="9999", ip="192.168.0.101", path="/cgi-bin/mjpg/video.cgi?subtype=1"):
    try:
        url = "http://" + user + ":" + password + "@" + ip + path
        vcap = cv2.VideoCapture(url)
        return vcap
    except:
        return "Exception: openVideoCapture"


def closeVideoCapture(vcap):
    vcap.release()


# noinspection PyBroadException
def getAngle(img, rx1, ry1, rx2, ry2):
    if img.all():
        cv2.imshow('tes', img)
        print("No Image")
        return
    region = img[rx1:rx2, ry1:ry2]
    cv2.rectangle(img, (ry1 - 1, rx1 - 1), (ry2, rx2), (0, 0, 255), 1)
    # convert to greyscale
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    # determining threshold for edges
    otsuVal, otsuImg = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # Detecting edges
    edges = cv2.Canny(gray, otsuVal * 0.5, otsuVal)
    # cv2.imshow('Edges', edges)
    try:
        # directions from edges
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180,
                                30,
                                minLineLength=20,
                                maxLineGap=50)
        # draws lines in image
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(region, (x1, y1), (x2, y2), (255, 0, 0), 1)
    except:
        cv2.putText(region, "No Line", (2, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
        return
    try:
        mean = np.mean(lines, axis=0)
        mean = mean[0]
        v = [mean[2] - mean[0], mean[1] - mean[3]]
        # angle in radians
        if v[0] == 0:
            angle = np.pi
        else:
            angle = np.arctan(v[1] / v[0])
        cv2.putText(region, "{:.2f}".format(angle * 180 / np.pi), (2, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
        mean = [int(x) for x in mean]
        cv2.line(region, (mean[0], mean[1]), (mean[2], mean[3]), (0, 255, 0), 3)
    except:
        cv2.putText(region, "No Angle", (2, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
        angle = None
    return angle


angles0 = np.zeros((5, 5))


def anglesBatteries(img, batpos=None, angles=angles0):
    if not batpos.all():
        width, height, channels = img.shape
        edgeX = 0.2 * width / 2
        edgeY = 0.2 * height / 2
        absX = 0.1 * width / 4
        absY = 0.1 * height / 4
        dHeight = 0.7 * width / 5
        dWidth = 0.7 * height / 5
        for i in range(5):
            for j in range(5):
                angles[i][j] = getAngle(img,
                                        int(edgeX + j * dHeight + absX * j),
                                        int(edgeY + i * dWidth + absY * i),
                                        int(edgeX + (j + 1) * dHeight + absX * j),
                                        int(edgeY + (i + 1) * dWidth + absY * i))
    else:
        for i in range(len(batpos)):
            for j in range(len(batpos[i])):
                angles[i][j] = getAngle(img, int(batpos[i][j][1]), int(batpos[i][j][0]), int(batpos[i][j][3]),
                                        int(batpos[i][j][2]))

    return img


def cv2ToTk(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
    return photo


def getTimeStamp(flag="%H-%M-%S.%f"):
    return datetime.now().strftime(flag)
