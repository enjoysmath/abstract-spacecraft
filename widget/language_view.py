from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
from graphics.language_canvas import LanguageCanvas
from graphics.object import Object
from graphics.arrow import Arrow
from bidict import bidict
from graphics.text import Text
from graphics.connectable import Connectable

class LanguageView(QGraphicsView):
    def __init__(self, canvas:LanguageCanvas):
        super().__init__(canvas)
        self._scale = (1.0, 1.0)
        self.setDragMode(self.RubberBandDrag)
        #self.setAcceptDrops(True)
        self._wheelZoom = True
        self._zoomFactor = (1.1, 1.1)
        self._zoomLimit = 25
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.init_scene_rect()
        self._name = None
        self._filename = None
        
    def __setstate__(self, data:dict):
        self.__init__(data['canvas'])
        self.setSceneRect(data['scene rect'])
        self.scale(*data['scale'])
        self._wheelZoom = data['wheel zoom']
        self._zoomFactor = data['zoom factor']
        self._zoomLimit = data['zoom limit']
        self._name = data['name']
        
    def __getstate__(self):
        data = {}
        data['canvas'] = self.scene()
        data['scale'] = self._scale
        data['scene rect'] = self.sceneRect()
        data['wheel zoom'] = self._wheelZoom
        data['zoom factor'] = self._zoomFactor
        data['zoom limit'] = self._zoomLimit
        data['name'] = self._name
        return data
    
    @property
    def filename(self):
        return self._filename
    
    def set_filename(self, filename:str):
        self._filename = filename
        
    @property
    def tab_name(self):
        return self._name
    
    def set_tab_name(self, name:str):
        self._name = name
        
    def init_scene_rect(self):
        screen = QGuiApplication.primaryScreen()
        geometry = screen.geometry()
        w = geometry.height()
        h = geometry.width()
        self.setSceneRect(0, 0, w, h)       
        
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            #self.setDragMode(self.ScrollHandDrag)
            pass
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setDragMode(self.RubberBandDrag)
        super().mouseReleaseEvent(event)
        
    def scale(self, sx, sy):
        s = self._scale
        super().scale(sx, sy)
        self._scale = (s[0]*sx, s[1]*sy)        

    def zoom_100(self):
        from core.geom_tools import extract_transform_scale
        transform = self.transform()
        sx, sy = extract_transform_scale(transform)
        self.setTransform(transform.scale(1.0/sx, 1.0/sy).scale(self._scale[0], self._scale[1]))    
        #IDK why this works...
        self.scale(1.0/self._scale[0], 1.0/self._scale[1])

    def zoom_in(self, times=None):
        if times is None:
            times = 1
        s = self._scale
        if s[0] < self._zoomLimit:
            z = self._zoomFactor
            s = (z[0]**times, z[1]**times)
        else:
            return 
        self.scale(*s)
        self.scene().update()   

    def zoom_out(self, times=None):
        if times is None:
            times = 1
        s = self._scale
        if s[0] > 1/self._zoomLimit:
            z = self._zoomFactor
            s = (1.0/z[0]**times, 1.0/z[1]**times)
        else:
            return   
        self.scale(*s)
        self.scene().update()           

    def wheelEvent(self, event):
        if self._wheelZoom:
            self.setTransformationAnchor(self.AnchorUnderMouse)
            #Scale the view / do the zoom
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else: 
                self.zoom_out()
        super().wheelEvent(event)        
    

        

        