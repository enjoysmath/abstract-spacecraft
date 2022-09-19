from PyQt5.QtWidgets import QApplication, QMenu
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

class Linkable:
    def __init__(self):
        self._link = None

    def _setState(self, data:dict):
        self._link = data['definition']
        
    def _getState(self, data:dict):
        data['definition'] = self._link
        return data
        
    def build_context_menu(self, menu:QMenu):
        if self._link is not None:
            menu.addAction('Definition').triggered.connect(lambda b: self.goto_link())
        menu.addAction('Set definition').triggered.connect(lambda b: self.user_navigates_to_link())
        
    def user_navigates_to_link(self):
        QApplication.instance().set_link_requester(linkable=self)
                    
    def goto_link(self):
        from gfx.language_gfx_view import LanguageGfxView
        
        if isinstance(self.link, str):
            QDesktopServices.openUrl(QUrl(self.link))
        elif isinstance(self.link, LanguageGfxView):
            window = self.link.window()
            window.raise_()
            window.navigate_to_language_view(self.link)
            
    def set_link(self, link):
        self._link = link
        
    @property
    def link(self):
        return self._link
                 
