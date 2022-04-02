from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMenu

class Deletable:
    delete_requested = pyqtSignal()
    
    def __init__(self):
        self._deletableByUser = True
        
    def _setState(self, data:dict):
        self._deletableByUser = data['deletable by user']
        
    def _getState(self, data:dict):
        data['deletable by user'] = self._deletableByUser
        return data
        
    @property
    def deletable_by_user(self):
        return self._deletableByUser 
    
    def delete(self):
        raise NotImplementedError
    
    def build_context_menu(self, menu:QMenu):
        if self.deletable_by_user:
            menu.addAction('Delete').triggered.connect(self.delete_requested.emit)
                    
        
    
    