from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QGuiApplication, QTransform
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from gfx.language_canvas import LanguageCanvas
from gfx.object import Object
from gfx.arrow import Arrow
from bidict import bidict
from gfx.text import Text
from gfx.connectable import Connectable

class LanguageGfxView(QGraphicsView):
    tab_name_changed = pyqtSignal(str)
    
    def __init__(self, canvas:LanguageCanvas):
        super().__init__(canvas)
        self._scale = (1.0, 1.0)
        self.setDragMode(self.RubberBandDrag)
        self.setSceneRect(QRectF())
        #self.setAcceptDrops(True)
        self._wheelZoom = True
        self._zoomFactor = 1.25
        self._zoomLimit = 25
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.init_scene_rect()
        self._name = None
        self._filename = None
        self.setSizePolicy(self.sizePolicy().Policy.Minimum, self.sizePolicy().Policy.Minimum)
        
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
        if self._name != name:
            self._name = name
            self.tab_name_changed.emit(name)        
        
    def init_scene_rect(self):
        screen = self.window()
        geometry = screen.geometry()
        w = geometry.height() // 4
        h = geometry.width() // 4           # BUGFIX: don't try this with actual screen or higher factors than this.
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
        self.setTransform(QTransform())
        #import geom_tools
        #transform = self.transform()
        #sx, sy = geom_tools.extract_transform_scale(transform)
        #self.setTransform(transform.scale(1.0/sx, 1.0/sy).scale(self._scale[0], self._scale[1]))    
        ##IDK why this works...
        #self.scale(1.0/self._scale[0], 1.0/self._scale[1])

    def zoom_in(self, cursorPos:QPointF=None):
        self._zoom(self._zoomFactor, cursorPos)
        
    def zoom_out(self, cursorPos:QPointF=None):
        self._zoom(1/self._zoomFactor, cursorPos)
        
    def _zoom(self, factor:float, cursorPos:QPointF=None):
        if cursorPos is None:
            cursorPos = self.mapFromGlobal(self.cursor().pos())
        # Set Anchors
        self.setTransformationAnchor(self.NoAnchor)
        self.setResizeAnchor(self.NoAnchor)    
        
        # Save the scene pos
        oldPos = self.mapToScene(cursorPos)
    
        self.scale(factor, factor)
    
        # Get the new position
        newPos = self.mapToScene(cursorPos)
    
        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())        
        
    def wheelEvent(self, event):
        # Zoom
        if event.angleDelta().y() > 0:
            self.zoom_in(event.pos())
        else:
            self.zoom_out(event.pos())
       
    def fit_contents_in_view(self):                
        self.setSceneRect(self.scene().itemsBoundingRect())
        
    def setParent(self, parent):
        super().setParent(parent)
        self.init_scene_rect()
        
    @property
    def language_canvases(self):
        return [self.scene()]
    
    def set_font(self, font, memo:dict=None):
        if memo is None:
            memo = {}
            
        if id(self) not in memo:
            memo[id(self)] = self
            
            for item in self.scene().items():
                if isinstance(item, Text):
                    item.setFont(font)    