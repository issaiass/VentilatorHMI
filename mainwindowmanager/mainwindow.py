import sys
import json
import os
import time
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from pyqtgraph import PlotWidget, plot
from PyQt5.QtCore import Qt, QThreadPool
from modelviewcontroller.ventmodel import VentModel
from threadmanager.threadhandler import ThreadHandler
from pyModbusTCP.client import ModbusClient

qt_creator_file = os.path.join('mainwindowmanager','mainwindow.ui')
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
plot_points = 100
time_interval = 50

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.model = VentModel() # settings file
        self.bconfirm.released.connect(self.confirm)
        self.bstart.released.connect(self.start)
        self.model.load()

        insptime, exptime, pressure = self.model.settings
        self.x1, self.x2, self.x3 = plot_points*[0], plot_points*[0], plot_points*[0]
        self.y1, self.y2, self.y3 = plot_points*[0.0], plot_points*[0.0], plot_points*[0.0]
        self.holding_registers = 3*[0]
        self.coil = False
        
        self.tnewinsp.setValue(insptime)
        self.tnewexp.setValue(exptime)
        self.newpress.setValue(pressure)

        self.tcurrinsp.setValue(insptime)
        self.tcurrexp.setValue(exptime)
        self.currpress.setValue(pressure)

        self.graph1 = pg.PlotWidget()
        self.graph2 = pg.PlotWidget()
        self.graph3 = pg.PlotWidget()
        self.vlgraphs.addWidget(self.graph1)
        self.vlgraphs.addWidget(self.graph2)
        self.vlgraphs.addWidget(self.graph3)

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line1 =  self.graph1.plot([], [], pen=pen)
        self.data_line2 =  self.graph2.plot([], [], pen=pen)
        self.data_line3 =  self.graph3.plot([], [], pen=pen)
        self.x1, self.y1 = self.graphInit(self.data_line1, plot_points)
        self.x1, self.y2 = self.graphInit(self.data_line2, plot_points)
        self.x1, self.y3 = self.graphInit(self.data_line3, plot_points)


        self.setStyle(self.graph1, 'Expiration vs time', 'Expiration', 'time (ms)')
        self.setStyle(self.graph2, 'Inspiration vs time', 'Inspiration', 'time (ms)')
        self.setStyle(self.graph3, 'Pressure vs time', 'Pressure', 'time (ms)')

        self.timer = QtCore.QTimer()
        self.timer.setInterval(time_interval)
        self.timer.timeout.connect(self.update_plot_data)


        self.modbuspool = QThreadPool()
        self.modbuswritepool = QThreadPool()

        self.modbustimer = QtCore.QTimer()
        self.modbustimer.setInterval(time_interval//2)
        self.modbustimer.timeout.connect(self.modbus_timer)
        self.modbustimer.start()



    def start(self):
        if self.bstart.text() == 'Start':
            self.timer.start()

            self.coil = True

            self.bstart.setText('Stop')

            self.holding_registers = 3*[0]
            self.x1, self.y1 = self.graphInit(self.data_line1, plot_points)
            self.x2, self.y2 = self.graphInit(self.data_line2, plot_points)
            self.x3, self.y3 = self.graphInit(self.data_line3, plot_points)

        elif self.bstart.text() == 'Stop':
            self.timer.stop()

            self.coil = False

            self.bstart.setText('Start')


        self.modbuswritepool.setMaxThreadCount(1)
        self.modbuswritetcp = ThreadHandler(self.modbus_write)
        self.modbuswritepool.start(self.modbuswritetcp)


    def confirm(self):
        insptime = self.tnewinsp.value()
        exptime = self.tnewexp.value()
        pressure = self.newpress.value()
        self.tcurrinsp.setValue(insptime)
        self.tcurrexp.setValue(exptime)
        self.currpress.setValue(pressure)
        self.model.settings = [insptime, exptime, pressure]
        self.model.save()



    def graphInit(self, dataline, pts):
        x = list(range(pts))  # 100 time points
        y = [0 for _ in range(pts)]  # 100 data points
        dataline.setData(x, y)  # Update the data.
        return x, y


    def update_plot_data(self):
        self.x1, self.y1 = self.update_points(self.data_line1, self.x1, self.y1)
        self.x2, self.y2 = self.update_points(self.data_line2, self.x2, self.y2)
        self.x3, self.y3 = self.update_points(self.data_line3, self.x3, self.y3)
        try:
            self.y1[-1] = self.holding_registers[0]/1000.0
            self.y2[-1] = self.holding_registers[1]/1000.0
            self.y3[-1] = self.holding_registers[2]/1000.0
        except TypeError:
            self.holding_registers = 3*[0]
            self.y1[-1] = self.holding_registers[0]/1000.0
            self.y2[-1] = self.holding_registers[1]/1000.0
            self.y3[-1] = self.holding_registers[2]/1000.0
            print("typeerror")

    def update_points(self, dataline, x, y):
        x = x[1:] 
        x.append(x[-1] + 1)
        y = y[1:]
        y.append(y[-1])
        dataline.setData(x, y)
        return x, y


    def setStyle(self, graph, title, labelx, labely):
        graph.setBackground('#000000')
        graph.setTitle(title, color='#0000FF')
        graph.setLabel('left', labelx, color='#00FF00')
        graph.setLabel('bottom', labely, color='#00FF00')

    def modbus_timer(self):
        self.modbuspool.setMaxThreadCount(1)
        self.modbustcp = ThreadHandler(self.modbus_request)
        self.modbuspool.start(self.modbustcp)


    def modbus_write(self, progress_callback):
        c = ModbusClient(host="localhost", auto_open=False)
        connection_ok = c.open()
        if connection_ok:
            try:
                c.write_single_coil(0, self.coil)
                c.close()
            except:
                print("modbus exception")
                pass
            else:
                print("other")
                pass
            finally:
                #print("passed")
                pass
        else:
            print("could not open")
            pass


    def modbus_request(self, progress_callback):
        c = ModbusClient(host="localhost", auto_open=False)
        connection_ok = c.open()
        if connection_ok:
            try:
                self.holding_registers = c.read_holding_registers(0,3)
                print(self.holding_registers)
                regs = [int(10*self.tcurrinsp.value()), 
                        int(10*self.tcurrexp.value()),
                        int(10*self.currpress.value())]
                c.write_multiple_registers(3, regs)
                print(regs)
                c.close()
            except:
                print("modbus exception")
                pass
            else:
                print("other")
                pass
            finally:
                #print("passed")
                pass
        else:
            print("could not open")
            pass