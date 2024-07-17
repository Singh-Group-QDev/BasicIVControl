import sys
from pymeasure.display.Qt import QtWidgets
from SdH.ExperimentOscillate import ExperimentOscillate
from SdH.ExperimentBackground import ExperimentBackground

app = QtWidgets.QApplication(sys.argv)
window = ExperimentOscillate()
#window = ExperimentBackground()
window.show()
sys.exit(app.exec())