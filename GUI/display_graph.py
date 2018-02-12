from pyqtgraph import QtCore, QtGui
import csv
import pyqtgraph as pg
from datetime import datetime
import sys
import numpy as np
import sched, time
import threading


NORMAL_FILE = "../Data/cs01_no_ls.csv"
RAS_FILE = "../Data/cs01_with_dufls_[VR].csv"

NORMAL_IMAGE = "../Data/normal_state.png"
ALERT_IMAGE = "../Data/alert_state.png"

WSU_LOGO = "Arpa_demo_nodes/RIAPS_Logo_list.png"
GA1_NORMAL = "Arpa_demo_nodes/Slide1.PNG"
SA1_NORMAL = "Arpa_demo_nodes/Slide2.PNG"
SA2_NORMAL = "Arpa_demo_nodes/Slide3.PNG"
GA1_RAS = "Arpa_demo_nodes/Slide4.PNG"
SA1_RAS = "Arpa_demo_nodes/Slide5.PNG"
SA2_RAS = "Arpa_demo_nodes/Slide6.PNG"

LINE_DIAGRAM = "Arpa_demo_nodes/14-bus-jing.png"

PLOT_SIZE = 500
TIMEOUT = 5

RANGE_MIN = 45
RANGE_MAX = 65

EMERGENCY_LIMIT = 59.78

class SpeedButton(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SpeedButton, self).__init__(parent=parent)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.speed = 1
        self.label = QtGui.QLabel(self)
        self.label.setText("Speed")
        self.verticalLayout.addWidget(self.label)

        self.sb1 = QtGui.QRadioButton("x1")
        self.sb1.toggled.connect(lambda: self.setSpeed(1))
        self.sb2 = QtGui.QRadioButton("x0.5")
        self.sb2.toggled.connect(lambda: self.setSpeed(0.5))
        self.sb3 = QtGui.QRadioButton("x0.25")
        self.sb3.toggled.connect(lambda: self.setSpeed(0.25))
        self.sb4 = QtGui.QRadioButton("x0.10")
        self.sb4.toggled.connect(lambda: self.setSpeed(0.1))

        self.verticalLayout.addWidget(self.sb1)
        self.verticalLayout.addWidget(self.sb2)
        self.verticalLayout.addWidget(self.sb3)
        self.verticalLayout.addWidget(self.sb4)

    def setSpeed(self, speed):
        self.speed = speed

    def getSpeed(self):
        return self.speed
        
class SystemStateWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SystemStateWidget, self).__init__(parent=parent)
        self.systemStateLayout = QtGui.QVBoxLayout(self)

        self.ga1Label = QtGui.QLabel(self)
        self.ga1NormalPixmap = QtGui.QPixmap(GA1_NORMAL).scaledToHeight(100)
        self.ga1RASPixmap = QtGui.QPixmap(GA1_RAS).scaledToHeight(100)
        self.ga1Label.setPixmap(self.ga1NormalPixmap)
        
        self.sa1Label = QtGui.QLabel(self)
        self.sa1NormalPixmap = QtGui.QPixmap(SA1_NORMAL).scaledToHeight(100)
        self.sa1RASPixmap = QtGui.QPixmap(SA1_RAS).scaledToHeight(100)
        self.sa1Label.setPixmap(self.sa1NormalPixmap)

        self.sa2Label = QtGui.QLabel(self)
        self.sa2NormalPixmap = QtGui.QPixmap(SA2_NORMAL).scaledToHeight(100)
        self.sa2RASPixmap = QtGui.QPixmap(SA2_RAS).scaledToHeight(100)
        self.sa2Label.setPixmap(self.sa2NormalPixmap)

        self.systemStateLayout.addWidget(self.ga1Label)
        self.systemStateLayout.addWidget(self.sa1Label)
        self.systemStateLayout.addWidget(self.sa2Label)

    def alert(self):
        self.ga1Label.setPixmap(self.ga1RASPixmap)
        self.sa1Label.setPixmap(self.sa1RASPixmap)
        self.sa2Label.setPixmap(self.sa2RASPixmap)

    def reset(self):
        self.ga1Label.setPixmap(self.ga1NormalPixmap)
        self.sa1Label.setPixmap(self.sa1NormalPixmap)
        self.sa2Label.setPixmap(self.sa2NormalPixmap)

class GraphWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent=parent)

        self.speed = 1
        self.index = 0

        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.w1 = SpeedButton()

#        self.w2 = Slider(-1, 1)
#        self.horizontalLayout.addWidget(self.w2)

#        self.w3 = Slider(-10, 10)
#        self.horizontalLayout.addWidget(self.w3)

#        self.w4 = Slider(-10, 10)
#        self.horizontalLayout.addWidget(self.w4)

        self.win = pg.GraphicsWindow(title="UFLS Demo")
        self.horizontalLayout.addWidget(self.win)
        #self.update()

        #self.w1.slider.valueChanged.connect(self.setInterval)

        self.normalReadings, self.rasReadings = self.parse_files()

        #Print the difference between times and see if there's any hope, or else take the average of times

        #time_list = [(self.normalTimes[i+1] - self.normalTimes[i]).microseconds for i in range(len(self.normalTimes) - 1) ]
        #print float(sum(time_list)/1000)/float(len(time_list))

        self.win.resize(1000, 600)

        pg.setConfigOptions(antialias = True)

        self.normalPlot = self.win.addPlot(title = "Without RAS")
        self.normalCurve = self.normalPlot.plot(pen = pg.mkPen('r', width = 3))
        self.normalPlot.setYRange(RANGE_MIN, RANGE_MAX, padding = 0.1, update = False)

        self.rasPlot = self.win.addPlot(title = "With RAS")
        self.rasCurve = self.rasPlot.plot(pen = pg.mkPen('b', width = 3))
        self.rasPlot.setYRange(58, 61, padding = 0.1, update = False)

        self.horizontalLayout.addWidget(self.w1)

        self.systemStateLayout = SystemStateWidget()
        
        self.horizontalLayout.addWidget(self.systemStateLayout)

        self.lineDiagramLabel = QtGui.QLabel(self)
        self.lineDiagramPixmap = QtGui.QPixmap(LINE_DIAGRAM)
        self.lineDiagramLabel.setPixmap(self.lineDiagramPixmap)

        self.horizontalLayout.addWidget(self.lineDiagramLabel)

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(TIMEOUT)


    def update(self):
        if self.index + PLOT_SIZE < len(self.normalReadings):
            self.normalCurve.setData(self.normalReadings[self.index : self.index+PLOT_SIZE])
            self.rasCurve.setData(self.rasReadings[self.index : self.index+PLOT_SIZE])
            self.index += 1
            if (self.speed != self.w1.getSpeed()):
                self.speed = self.w1.getSpeed()
                self.timer.setInterval(int(TIMEOUT/self.speed))
            if self.normalReadings[self.index] < EMERGENCY_LIMIT:
                self.systemStateLayout.alert()
        else:
            self.systemStateLayout.reset()
            self.index = 0
        

    def setInterval(self):
        self.interval = self.w1.x

    def parse_files(self):

        normalFile = open(NORMAL_FILE, 'r') 
        rasFile = open(RAS_FILE, 'r')

        normalReader = csv.reader(normalFile)
        rasReader = csv.reader(rasFile)

        normalReadings = list()
        rasReadings = list()

        normalTimes = list()
        rasTimes = list()

        for row in normalReader:
            normalReadings.append(float(row[1].strip()))
        
            #Get all the dates and times and then display them
            #normalTimes.append(datetime.strptime(row[0].strip(), '%m/%d/%Y %X.%f'))
        
        for row in rasReader:
            rasReadings.append(float(row[1].strip()))
            #rasTimes.append(datetime.strptime(row[0].strip(), '%m/%d/%Y %X.%f'))


        normalFile.close()
        rasFile.close()

        print len(normalReadings)
        print len(rasReadings)

        return normalReadings[-5000:], rasReadings[-5000:]


class DemoWindow(QtGui.QWidget):
    def __init__(self, parent = None):
        super(DemoWindow, self).__init__(parent = parent)

        self.graph = GraphWidget(self)

        
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.graph)


        self.logoPixmap = QtGui.QPixmap(WSU_LOGO)
        self.logoLabel = QtGui.QLabel(self)
        self.logoLabel.setPixmap(self.logoPixmap.scaledToHeight(100))
        self.verticalLayout.addWidget(self.logoLabel)




if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = DemoWindow()
    w.show()
    sys.exit(app.exec_())


