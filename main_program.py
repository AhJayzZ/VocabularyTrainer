from PyQt5.QtWidgets import *
from UI.Ui_init import *
import sys,socket
from UI.mainUI import *


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VocabularyTrainer()
    win.show()
    sys.exit(app.exec_())