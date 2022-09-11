from PyQt5.QtCore import *

class DragDroppable:
    def __init__(self):
        self.setAcceptDrops(True)
        
    def _setState(self, data):
        pass
    
    def _getState(self, data):
        pass
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/octet-stream'):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        pass
    
    def dropEvent(self, event):
        print(event.mimeData().text())
        
    def use_another_drag_item(self):
        return self