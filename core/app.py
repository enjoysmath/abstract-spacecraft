from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from dialog.mainwindow import MainWindow
from gfx.linkable import Linkable
from PyQt5.QtCore import Qt
from dialog.set_definition_dialog import SetDefinitionDialog
from dialog.font_dialog import FontDialog
from gfx.text import Text
import os
import _pickle as pickle


class App(QApplication):    
    last_session = 'last_session.pickle'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._windows = []
        self._setDefDialog = SetDefinitionDialog()
        self._appFontDialog = FontDialog()
        self._appFontDialog.font_changed.connect(self.setFont)
        self._appFontDialog.setWindowTitle('Set app font')
        self._appDataPath = None
        self._saved = False
        self._quit = False
        
    def show_app_font_dialog(self):
        self._appFontDialog.exec_()
        
    def show_set_definition_dialog(self, linkable:Linkable):
        self._setDefDialog.show(linkable)
        
    def topmost_main_window(self):
        topLevel = self.topLevelWidgets()
        for widget in topLevel:
            if isinstance(widget, MainWindow):
                return widget
        
    def add_new_window(self):
        window = MainWindow()
        self._windows.append(window)
        window.show()
        return window
        
    def setFont(self, font):
        super().setFont(font)
        for window in self._windows:
            for langView in window.language_views():
                for item in langView.scene().items():
                    if isinstance(item, Text):
                        item.setFont(font)
        self._appFontDialog.set_font(font)
        
    def load_app_pickle(self, data:dict):
        for window in data['windows']:
            self._windows.append(window)
            window.show()
            
    def save_app_pickle(self):
        return {
            'windows' : self._windows,
        }
    
    def load_last_session_or_blank(self):
        status_msg = "Ready."
        
        try:            
            if not os.path.exists(self.last_session):
                raise FileNotFoundError(f"The last session file at '{self.last_session}' does not exist. Loading blank window")
            
            last_project_path = None
        
            with open(self.last_session, "rb") as file:
                last_project_path = pickle.load(file)
                
            if not os.path.exists(last_project_path):
                raise FileNotFoundError(f"The project at '{last_project_path}' no longer exists. Loading blank window.")
            
            with open(last_project_path, "rb") as file:
                data = pickle.load(file)
                self.load_app_pickle(data)
                self._appDataPath = last_project_path
                self.set_saved()
    
        except Exception as excep:
            status_msg = str(excep)
            self.add_new_window()
            self.set_saved(False)
            #if __debug__:
                #raise excep
            
        self.broadcast_status_message(status_msg, 5000)        
        
    def broadcast_status_message(self, status_msg:str, timeout_ms:int):
        for window in self._windows:
            window.statusBar().showMessage(status_msg, timeout_ms)
            
    def set_saved(self, saved:bool=True):
        if self._saved != saved:
            self._saved = saved
            
            for window in self._windows:
                window.set_saved_title(saved)
                
    def is_saved(self):
        return self._saved
    
    def load_app_data(self, filename:str=None):
        if filename is None:
            filenames,_ = QFileDialog.getOpenFileNames(self.topmost_main_window(), 'Open Diagrams', './standard_library', 'Abstract Spacecraft (*.🌌)')
        for filename in filenames:            
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            self.load_app_pickle(data)
            self._appDataPath = filename
            self.set_saved()
    
    def save_app_data(self, filename:str=None):
        if not filename:
            filename = self._appDataPath
        
        if not filename:
            self.save_app_data_as()
            return 
        
        with open(filename, 'wb') as file:
            pickle.dump(self.save_app_pickle(), file=file)
            self.set_saved()
            
    def save_app_data_as(self):
        filename,_ = QFileDialog.getSaveFileName(self.topmost_main_window(), 'Save Diagrams As', './standard_library', 'Abstract Spacecraft (*.🌌)')
        
        if filename:
            self.save_app_data(filename)
            self._appDataPath = filename
            
    def documents_from_app_data(self, filname):
        status_msg = "Ready."
        
        try:        
            with open(self.last_session, "rb") as file:
                last_project_path = pickle.load(file)
                
            if not os.path.exists(last_project_path):
                raise FileNotFoundError(f"The project at '{last_project_path}' no longer exists. Loading blank window.")
            
            with open(last_project_path, "rb") as file:
                data = pickle.load(file)
                self.load_app_pickle(data)
                self._appDataPath = last_project_path
                self.set_saved()
    
        except Exception as excep:
            status_msg = str(excep)
            self.add_new_window()
            self.set_saved(False)
                
    def quit(self):
        if not self._quit:
            self.save_last_session()
            self._quit = True
            super().quit()
            
    
    def save_last_session(self):        
        try:            
            last_project_path = self._appDataPath
            
            if not last_project_path:
                return
            
            with open(self.last_session, "wb") as file:
                pickle.dump(last_project_path, file)
    
        except Exception as excep:
            raise excep      