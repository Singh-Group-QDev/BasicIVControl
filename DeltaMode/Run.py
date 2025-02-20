import sys
from pymeasure.display.Qt import QtWidgets
from DeltaMode.ExperimentDeltaTest import ExperimentDeltaTest

app = QtWidgets.QApplication(sys.argv)

window = ExperimentDeltaTest()

window.show()
sys.exit(app.exec())