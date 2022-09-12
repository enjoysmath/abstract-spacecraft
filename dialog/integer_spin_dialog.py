from PyQt5.QtWidgets import QDialog
from ui.ui_integer_spin_dialog import Ui_IntegerSpinDialog

class IntegerSpinDialog(QDialog, Ui_IntegerSpinDialog):
    def __init__(self):
        QDialog.__init__(self)
        Ui_IntegerSpinDialog.__init__(self)
        self.setupUi(self)
           
    def exec_(self):
        previous = self.spinBox.value()
        result = super().exec_()
        
        if result == self.Rejected:
            self.spinBox.setValue(previous)
            
        return result
            