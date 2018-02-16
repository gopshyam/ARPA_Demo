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
GA1_ALERT = "Arpa_demo_nodes/Slide2.PNG"
GA1_STABLE = "Arpa_demo_nodes/Slide3.PNG"
SA1_NORMAL = "Arpa_demo_nodes/Slide4.PNG"
SA1_ALERT = "Arpa_demo_nodes/Slide5.PNG"
SA1_STABLE = "Arpa_demo_nodes/Slide6.PNG"
SA2_NORMAL = "Arpa_demo_nodes/Slide7.PNG"
SA2_ALERT = "Arpa_demo_nodes/Slide8.PNG"
SA2_STABLE = "Arpa_demo_nodes/Slide9.PNG"

LINE_DIAGRAM = "Arpa_demo_nodes/14-bus-jing.png"

PLOT_SIZE = 500
TIMEOUT = 5

INITIAL_VALUE = 60.0

EMERGENCY_LIMIT = 59.78

RANGE_START = 0
RANGE_END = 500
RANGE_LIMIT = 10000000



def parse_files():

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


        return normalReadings[750:], rasReadings[-7700:]



class DataGenerator():
    def __init__(self):
        self.normalReadings, self.rasReadings = parse_files()
        self.index = 0
        self.isContingency = False

    def start(self):
        self.isContingency = True

    def stop(self):
        self.isContingency = False
        self.index = 0

    def get(self):
        normalReading = INITIAL_VALUE
        rasReading = INITIAL_VALUE

        if (self.isContingency):
            normalReading = self.normalReadings[self.index]
            rasReading = self.rasReadings[self.index]

            self.index += 1

            if self.index >= len(self.normalReadings):
                self.index = 0

        return normalReading, rasReading



class SpeedButton(QtGui.QWidget):
    def __init__(self, dataGenerator, parent=None):
        super(SpeedButton, self).__init__(parent=parent)


        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.speed = 0.25
        self.label = QtGui.QLabel(self)
        self.label.setText("Speed")
        self.label.setFixedHeight(25)

        self.startButton = QtGui.QPushButton('Apply Contingency', self)
        self.startButton.clicked.connect(dataGenerator.start)

        self.stopButton = QtGui.QPushButton('Reset', self)
        self.stopButton.clicked.connect(dataGenerator.stop)

        self.fullPlotButton = QtGui.QPushButton("View Full Plot", self)

        self.sb1 = QtGui.QRadioButton("x1")
        self.sb1.toggled.connect(lambda: self.setSpeed(1))
        self.sb2 = QtGui.QRadioButton("x0.5")
        self.sb2.toggled.connect(lambda: self.setSpeed(0.5))
        self.sb3 = QtGui.QRadioButton("x0.25")
        self.sb3.toggled.connect(lambda: self.setSpeed(0.25))
        self.sb3.setChecked(True)
        self.sb4 = QtGui.QRadioButton("x0.10")
        self.sb4.toggled.connect(lambda: self.setSpeed(0.1))

        #self.speedLayout = QtGui.QVBoxLayout()
        #self.speedLayout.addWidget(self.label)
        #self.speedLayout.addWidget(self.sb1)
        
        print self.label.frameGeometry().width()

        self.verticalLayout.addWidget(self.startButton)
        self.verticalLayout.addWidget(self.stopButton)
        self.verticalLayout.addWidget(self.fullPlotButton)
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.sb1)
        self.verticalLayout.addWidget(self.sb2)
        self.verticalLayout.addWidget(self.sb3)
        self.verticalLayout.addWidget(self.sb4)
        #self.verticalLayout.addLayout(self.speedLayout)


    def setSpeed(self, speed):
        self.speed = speed

    def getSpeed(self):
        return self.speed
        
class SystemStateWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SystemStateWidget, self).__init__(parent=parent)
        self.systemStateLayout = QtGui.QVBoxLayout(self)

        height = 200

        if (parent):
            height = parent.frameGeometry().width() * 2.5
            print height

        self.isAlert = False

        self.ga1Label = QtGui.QLabel(self)
        self.ga1NormalPixmap = QtGui.QPixmap(GA1_NORMAL).scaledToHeight(height)
        self.ga1AlertPixmap = QtGui.QPixmap(GA1_ALERT).scaledToHeight(height)
        self.ga1StablePixmap = QtGui.QPixmap(GA1_STABLE).scaledToHeight(height)
        self.ga1Label.setPixmap(self.ga1NormalPixmap)
        
        self.sa1Label = QtGui.QLabel(self)
        self.sa1NormalPixmap = QtGui.QPixmap(SA1_NORMAL).scaledToHeight(height)
        self.sa1AlertPixmap = QtGui.QPixmap(SA1_ALERT).scaledToHeight(height)
        self.sa1StablePixmap = QtGui.QPixmap(SA1_STABLE).scaledToHeight(height)
        self.sa1Label.setPixmap(self.sa1NormalPixmap)

        self.sa2Label = QtGui.QLabel(self)
        self.sa2NormalPixmap = QtGui.QPixmap(SA2_NORMAL).scaledToHeight(height)
        self.sa2AlertPixmap = QtGui.QPixmap(SA2_ALERT).scaledToHeight(height)
        self.sa2StablePixmap = QtGui.QPixmap(SA2_STABLE).scaledToHeight(height)
        self.sa2Label.setPixmap(self.sa2NormalPixmap)

        self.systemStateLayout.addWidget(self.ga1Label)
        self.systemStateLayout.addWidget(self.sa1Label)
        self.systemStateLayout.addWidget(self.sa2Label)

    def alert(self):
        self.isAlert = True
        self.ga1Label.setPixmap(self.ga1AlertPixmap)
        self.sa1Label.setPixmap(self.sa1AlertPixmap)
        self.sa2Label.setPixmap(self.sa2AlertPixmap)

    def reset(self):
        self.isAlert = False
        self.ga1Label.setPixmap(self.ga1NormalPixmap)
        self.sa1Label.setPixmap(self.sa1NormalPixmap)
        self.sa2Label.setPixmap(self.sa2NormalPixmap)

    def stable(self):
        self.isAlert = False
        self.ga1Label.setPixmap(self.ga1StablePixmap)
        self.sa1Label.setPixmap(self.sa1StablePixmap)
        self.sa2Label.setPixmap(self.sa2StablePixmap)


class GraphWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent=parent)

        self.speed = 1
        self.index = 0

        self.horizontalLayout = QtGui.QHBoxLayout(self)

        self.dataGenerator = DataGenerator()
        self.w1 = SpeedButton(self.dataGenerator)
        self.w1.fullPlotButton.clicked.connect(self.showFullPlot)

#        self.w2 = Slider(-1, 1)
#        self.horizontalLayout.addWidget(self.w2)

#        self.w3 = Slider(-10, 10)
#        self.horizontalLayout.addWidget(self.w3)

#        self.w4 = Slider(-10, 10)
#        self.horizontalLayout.addWidget(self.w4)

        self.win = pg.GraphicsWindow(title="UFLS Demo")
        #self.update()

        #self.w1.slider.valueChanged.connect(self.setInterval)

        self.normalReadings = [60.0 for _ in range(PLOT_SIZE)]
        self.rasReadings = [60.0 for _ in range(PLOT_SIZE)]


        #Print the difference between times and see if there's any hope, or else take the average of times

        #time_list = [(self.normalTimes[i+1] - self.normalTimes[i]).microseconds for i in range(len(self.normalTimes) - 1) ]
        #print float(sum(time_list)/1000)/float(len(time_list))

        self.win.resize(1000, 600)

        pg.setConfigOptions(antialias = True)

        self.horizontalLayout.addWidget(self.win)

        self.rangeStart = 0
        self.rangeEnd = 500

        self.normalPlot = self.win.addPlot(title = "Without RAS")
        self.normalCurve = self.normalPlot.plot(pen = pg.mkPen('r', width = 3))
        self.normalPlot.setYRange(49, 60, padding = 0.1, update = False)
        self.normalPlot.setLabel("left", "Frequency", units = "Hz")
        self.normalPlot.setLabel("bottom", "Time", units = "ms")

        self.rasPlot = self.win.addPlot(title = "With RAS")

        index_list = map(str, range(500, 1000))
        index_dict = dict(enumerate(index_list))
        self.rasPlot.getAxis('bottom').setTicks([[(0, '500'), (100, '600'), (200, '700'), (300, '800'), (400, '900'), (500, '1000')]])
        print index_dict.items()

        self.rasCurve = self.rasPlot.plot(pen = pg.mkPen('b', width = 3))
        self.rasPlot.setYRange(58.1, 60, padding = 0.1, update = False)
        self.rasPlot.setLabel("left", "Frequency", units = "Hz")
        self.rasPlot.setLabel("bottom", "Time", units = "ms")

        

        self.horizontalLayout.addWidget(self.w1)

        self.systemStateLayout = SystemStateWidget(self)
        
        self.horizontalLayout.addWidget(self.systemStateLayout)

        self.lineDiagramLabel = QtGui.QLabel(self)
        self.lineDiagramPixmap = QtGui.QPixmap(LINE_DIAGRAM)
        self.lineDiagramLabel.setPixmap(self.lineDiagramPixmap)

        self.horizontalLayout.addWidget(self.lineDiagramLabel)

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(TIMEOUT)


    def update(self):
        normalReading, rasReading = self.dataGenerator.get()
        self.normalReadings = self.normalReadings[1:] + [normalReading]
        self.rasReadings = self.rasReadings[1:] + [rasReading]
        self.normalCurve.setData(self.normalReadings)
        self.rasCurve.setData(self.rasReadings)

        self.rangeStart = self.rangeStart + 1
        self.rangeEnd = self.rangeEnd + 1
        if (self.rangeEnd > RANGE_LIMIT):
            self.rangeStart = RANGE_START
            self.rangeEnd = RANGE_END

        #self.rasPlot.setXRange(self.rangeStart, self.rangeEnd)

        if (self.speed != self.w1.getSpeed()):
            self.speed = self.w1.getSpeed()
            self.timer.setInterval(int(TIMEOUT/self.speed))

        if self.rasReadings[-1] < EMERGENCY_LIMIT:
            self.systemStateLayout.alert()
        else:
            if self.systemStateLayout.isAlert:
                self.systemStateLayout.stable()
            
        
    def showFullPlot(self):
        self.timer.setInterval(5000)
        self.speed = 0.2
        normalReadings, rasReadings = parse_files()
        self.normalCurve.setData(normalReadings)
        self.rasCurve.setData(rasReadings[:len(normalReadings)])

    def setInterval(self):
        self.interval = self.w1.x

    
class DemoWindow(QtGui.QWidget):
    def __init__(self, parent = None):
        super(DemoWindow, self).__init__(parent = parent)
        self.showMaximized()

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


