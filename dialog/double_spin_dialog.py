from PyQt5.QtWidgets import QDialog
from ui.ui_double_spin_dialog import Ui_DoubleSpinDialog

class DoubleSpinDialog(QDialog, Ui_DoubleSpinDialog):
    def __init__(self):
        QDialog.__init__(self)
        Ui_DoubleSpinDialog.__init__(self)
        self.setupUi(self)
    
    def exec_(self):
        previous = self.doubleSpinBox.value()
        result = super().exec_()
        
        if result == self.Rejected:
            self.doubleSpinBox.setValue(previous)
            
        return result    