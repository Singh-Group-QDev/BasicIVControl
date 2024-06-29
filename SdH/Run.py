import sys
from pymeasure.display.Qt import QtWidgets
from SdH.ExperimentOscillate import ExperimentOscillate

app = QtWidgets.QApplication(sys.argv)
window = ExperimentOscillate()
# window = ExperimentCurrent()
window.show()
sys.exit(app.exec())