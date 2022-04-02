from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtGui import QIcon

class ColorDialog(QColorDialog):
    def __init__(self, title:str=None):
        super().__init__()
        if title:
            self.setWindowTitle(title)
        self.setWindowIcon(QIcon(":/img/galaxy.ico"))
        self.setOption(self.ShowAlphaChannel, on=True)

    def __setstate__(self, data:dict):
        self.__init__()
        self._setState(data)
    
    def _setState(self, data:dict):
        self.setWindowTitle(data['title'])
        self.setCurrentColor(data['current color'])
        k = 0
        for color in data['custom colors']:
            self.setCustomColor(k, color)
            k += 1
        
    def __getstate__(self) -> dict:
        data = self._getState({})
        return data
    
    def _getState(self, data:dict) -> dict:
        data['current color'] = self.currentColor()
        data['title'] = self.windowTitle()
        data['custom colors'] = [self.customColor(k) for k in range(self.customCount())]
        return data
    
    def exec_(self):
        previous = self.currentColor()
        result = super().exec_()
        
        if result == self.Rejected:
            self.setCurrentColor(previous)
            
        return result    