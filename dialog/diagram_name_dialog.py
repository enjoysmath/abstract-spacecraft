from PyQt5.QtWidgets import QDialog
from ui.ui_diagram_name_dialog import Ui_DiagramNameDialog
from PyQt5.QtCore import Qt

class DiagramNameDialog(QDialog, Ui_DiagramNameDialog):  
    def __init__(self):
        QDialog.__init__(self)
        Ui_DiagramNameDialog.__init__(self)
        self.setupUi(self)
        #self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
