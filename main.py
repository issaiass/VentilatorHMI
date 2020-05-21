import sys
import os
from PyQt5 import QtWidgets
from mainwindowmanager.mainwindow import MainWindow

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())