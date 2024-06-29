import sys
from pymeasure.display.Qt import QtWidgets
from IV.ExperimentCurrent import ExperimentCurrent
from IV.ExperimentIV2 import ExperimentIV2

app = QtWidgets.QApplication(sys.argv)
window = ExperimentIV2()
# window = ExperimentCurrent()
window.show()
sys.exit(app.exec())