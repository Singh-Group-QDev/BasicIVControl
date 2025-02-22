import sys
from pymeasure.display.Qt import QtWidgets
from SdH.ExperimentOscillate import ExperimentOscillate
from SdH.ExperimentBackground import ExperimentBackground
from SdH.ExperimentOscillateAC import ExperimentOscillateAC
from SdH.ExperimentRxy import ExperimentRxy
from SdH.ExperimentACDC import ExperimentACDC
from SdH.ExperimentInverse import ExperimentInverse

app = QtWidgets.QApplication(sys.argv)
window = ExperimentOscillateAC()
#window = ExperimentOscillate()
#window = ExperimentBackground()
#window = ExperimentRxy()
#window = ExperimentACDC()
#window = ExperimentInverse()
window.show()
sys.exit(app.exec())