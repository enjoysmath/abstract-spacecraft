from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMenu

class Definable:
    def __init__(self):
        self._definition = None

    def _setState(self, data:dict):
        self._definition = data['definition']
        
    def _getState(self, data:dict):
        data['definition'] = self._definition
        return data
        
    def build_context_menu(self, menu:QMenu):
        if self._definition is not None:
            menu.addAction('Definition').triggered.connect(lambda b: self.goto_definition())
        menu.addAction('Set definition').triggered.connect(lambda b: self.user_navigates_to_definition())
        
    def user_navigates_to_definition(self):
        QApplication.instance().show_set_definition_dialog(definable=self)
                    
    def goto_definition(self):
        window = self._definition.window()
        window.raise_()
        window.navigate_to_language_view(self._definition)
        
            
    def set_definition(self, definition):
        self._definition = definition
        
    @property
    def definition(self):
        return self._definition
                 
