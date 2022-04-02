from PyQt5.QtWidgets import QGraphicsView, QUndoStack
from PyQt5.QtCore import Qt, pyqtSignal, QByteArray, QMimeData, QPointF, QRectF
from PyQt5.QtGui import QDrag, QCursor
from copy import deepcopy
from core.geom_tools import min_bounding_rect
import dill as pickle
import core.app
from undo_commands.drop_undo import DropUndo
from widget.node import Node
from core.qt_tools import set_pixmap_opacity

class View(QGraphicsView):
    focused = pyqtSignal()
    focusedOut = pyqtSignal()
    drop_requested = pyqtSignal(list)
    drop_into_parent_requested = pyqtSignal(list, Node)
    orphan_items_requested = pyqtSignal(list)    
    
    def __init__(self, scene=None, new=True):
        super().__init__()
        self._scale = (1.0, 1.0)
        if new:
            self._wheelZoom = True
            self._zoomFactor = (1.1, 1.1)
            self._zoomLimit = 25
            if scene:
                self.setScene(scene)
            View.setup(self)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self._styleWidget = None
        self._labelWidget = None
        self._searchWidget = None
        self._orphanItems = None
        
    def __setstate__(self, data):
        self.__init__(new=False)
        self.setScene(data["scene"])
        self._zoomFactor = data["zoom factor"]
        self._zoomLimit = data["zoom limit"]
        self._wheelZoom = data["wheel zoom"]
        self.scale(*data["scale"])
        View.setup(self)
    
    def __getstate__(self):
        return {
            "scene" : self.scene(),
            "zoom factor" : self._zoomFactor,
            "zoom limit" : self._zoomLimit,
            "wheel zoom" : self._wheelZoom,
            "scale" : self._scale,
        }
    
    def __deepcopy__(self):
        copy = type(self)(new=False)
        memo[id(self)] = self
        copy.setScene(deepcopy(self.scene()))
        copy._zoomFactor = self._zoomFactor
        copy._zoomLimit = self._zoomLimit
        copy._wheelZoom = self._wheelZoom
        copy.scale(self._scale)   
        View.setup(copy)
        return copy
    
    def setup(self):
        pass
        # self.fit_contents()    # PATCH / HACKFIX.  Diagram shows up blank white, unless we fit_contents()
        
    def setStyleWidget(self, widget):
        self._styleWidget = widget
        
    def styleWidget(self):
        return self._styleWidget
    
    def setLabelWidget(self, widget):
        self._labelWidget = widget
        
    def labelWidget(self):
        return self._labelWidget
        
    def window(self):
        return self._window
    
    def setUndoView(self, view):
        self._undoView = view
        
    def scaleX(self):
        return self._scale[0]
    
    def scaleY(self):
        return self._scale[1]
            
    def scale(self, sx, sy):
        s = self._scale
        super().scale(sx, sy)
        self._scale = (s[0]*sx, s[1]*sy)        
                
    def zoom_100(self):
        import core.geom_tools
        transform = self.transform()
        sx, sy = core.geom_tools.extract_transform_scale(transform)
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
          
    def focusInEvent(self, event):
        self.focused.emit()
        super().focusInEvent(event)    
        
    def focusOutEvent(self, event):
        self.focusedOut.emit()
        super().focusOutEvent(event)
        
    def mousePressEvent(self, event):
        if core.app.inst.keyboardModifiers() & Qt.ShiftModifier:
            items = self.scene().selectedItems()
            items = list(self.filter_drag_items(items))
            if items:
                if core.app.inst.keyboardModifiers() & Qt.AltModifier:
                    self._orphanItems = items
                                   
                try:
                    #if pickle.pickles(items):
                    min_rect = self.min_rect_of_items(items)
                    top_left = min_rect.topLeft()
                    top_left = self.mapFromScene(top_left)
                    
                    pixmap = self.grab_pixmap_of_items(items, opacity=core.app.inst.drag_and_drop_opacity)
                    if pixmap:
                        item_data = QByteArray(pickle.dumps(items))
                        mime_data = QMimeData()
                        mime_data.setData(core.app.inst.data_mime_type, item_data)
                        drag = QDrag(self)
                        drag.setMimeData(mime_data)
                        drag.setPixmap(pixmap)
                        drag.setHotSpot(event.pos() - top_left)
                        
                        if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
                            pass           
                except Exception as e:
                    if __debug__:
                        raise e
                    #app.inst.warning(excep=e, msg='Unable to drag and drop a ' + child.__class__.__name__)
            else:
                super().mouseMoveEvent(event)
        else:
            super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        self._orphanItems = None
        super().mouseReleaseEvent(event)
                        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(core.app.inst.data_mime_type):
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
            else:
                event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(core.app.inst.data_mime_type):
            if event.source() is self:
                if self._orphanItems:
                    self.orphan_items_requested.emit(self._orphanItems)                        
                    self._orphanItems = None
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if event.mimeData().hasFormat(core.app.inst.data_mime_type):
            data = event.mimeData().data(core.app.inst.data_mime_type).data()
            drop = pickle.loads(data)
            center = QPointF()
            
            for item in drop:
                center += item.scenePos()
            
            pos = self.mapToScene(event.pos())
            center /= len(drop)
            delta = pos - center
            
            for item in drop:
                item.set_scene_pos(item.pos() + delta)
            
            items = self.scene().items(pos)
            for item in items:
                if isinstance(item, Node):
                    self.drop_into_parent_requested.emit(drop, item)
                    break
            else:
                self.drop_requested.emit(drop)
                
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
            else:
                event.setDropAction(Qt.CopyAction)
                
            event.accept()
            self.fit_contents()             # HACKFIX.  
        else:
            event.ignore()
            
    def grab_pixmap_of_items(self, items, opacity=None):
        from core.geom_tools import min_bounding_rect
        rect = QRectF()
        for i in items:
            rect = rect.united(i.mapToScene(i.boundingRect()).boundingRect())
        rect = self.mapFromScene(rect).boundingRect()
        pixmap = self.grab(rect)
        if opacity is not None:
            pixmap = set_pixmap_opacity(pixmap, opacity)
        return pixmap
    
    def filter_drag_items(self, items):
        prev_set = { id(i) : i for i in items }
        filtered = self._filterDragItems(prev_set)
        while filtered != prev_set:
            prev_set = filtered
            filtered = self._filterDragItems(filtered)
        return filtered.values()       
        
    def _filterDragItems(self, items):
        I = dict(items)
        from widget.banana_cats import BananaCats
        for k,i in items.items():
            if not isinstance(i, BananaCats):
                del I[k]
                continue
            p = i.parentItem()
            if p and id(p) in I:
                del I[k]
            elif hasattr(i, 'ignore_drag') and i.ignore_drag():
                del I[k]
            elif hasattr(i, 'drag_instead'):
                j = i.drag_instead()
                if j:
                    del I[k]
                    I[id(j)] = j                
        return I
        
    def min_rect_of_items(self, items):
        min_rect = []
        for i in items:
            # Adjusting the bounding rect for proper pixmap doesn't work here for some reason...
            rect = i.boundingRect()
            rect = i.mapToScene(rect).boundingRect()
            min_rect.append(rect)
        min_rect = min_bounding_rect(min_rect)
        return min_rect
    
    def set_select_mode(self, en):
        if en:
            self.setDragMode(self.RubberBandDrag)
        else:
            self.setDragMode(self.ScrollHandDrag)  
            
    def select_mode(self):
        if self.dragMode() == self.RubberBandDrag:
            return True
        elif self.dragMode() == self.ScrollHandDrag:
            return False
        
    def fit_contents(self):
        items = self.scene().items()
        rect = QRectF()
        for item in items:
            rect = rect.united(item.mapToScene(item.boundingRect()).boundingRect())
        rect.setTopLeft(QPointF(-rect.width()/2, -rect.height()/2))
        self.setSceneRect(rect)