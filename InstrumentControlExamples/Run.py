import sys
from pymeasure.display.Qt import QtWidgets
from InstrumentControlExamples.ExperimentRandom import RandomExperiment

app = QtWidgets.QApplication(sys.argv)
window = RandomExperiment()
#window = IVExperiment()
window.show()
sys.exit(app.exec())