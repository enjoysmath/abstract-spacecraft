from PyQt5.QtGui import QFontMetrics, QPainter, QColor
from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt, QPointF, QRectF, QEvent
from connectable import Connectable
from container import Container
from text import Text
from qt_tools import SimpleBrush, Pen
from color_fillable import ColorFillable
from collision_responsive import CollisionResponsive
from containable import Containable
from graphics_shape import GraphicsShape
from bounded import Bounded
from drag_droppable import DragDroppable
from snappable import Snappable
from has_context_menu import HasContextMenu
from deletable import Deletable
from geom_tools import closest_point_on_path

class Object(GraphicsShape, Bounded, Connectable, Container, CollisionResponsive, ColorFillable, \
             DragDroppable, Containable, Snappable, HasContextMenu, Deletable):
    render_hints = QPainter.Antialiasing        # E.g. try QPainter.HighQualityAntialiasing
    
    default_fill_color = Qt.transparent
    default_border_color = Qt.transparent
    default_border_width = 2.0
    default_corner_radius = 16.0
    
    def __init__(self, text:str=None):
        GraphicsShape.__init__(self)
        Bounded.__init__(self)
        Connectable.__init__(self)
        Container.__init__(self)
        CollisionResponsive.__init__(self)
        ColorFillable.__init__(self)
        DragDroppable.__init__(self)
        Containable.__init__(self)
        Snappable.__init__(self)
        HasContextMenu.__init__(self)
        Deletable.__init__(self)
        self.setFlags(self.ItemIsFocusable | self.ItemIsSelectable | self.ItemIsMovable | self.ItemSendsGeometryChanges)
        self._cornerRadius = self.default_corner_radius
        self.setFiltersChildEvents(True)
        if text is not None:
            text = Text(text)
            text.setParentItem(self)
            text.set_snap_to_grid(True)
            text.setPos(-text.boundingRect().center())
            text.installSceneEventFilter(self)
            text.setFlag(text.ItemIsMovable, False)
            #metrics = QFontMetrics(text.font())
            #w = metrics.width(text.toPlainText()) + self._bboxPad/2
            #h = metrics.height() + self._bboxPad/2
            #text.setPos(QPointF(-w/2, -h/2))
            #text.setTransformOriginPoint(QPointF(w/2, h/2))
        self.set_brush_color(self.default_fill_color)
        self.setPen(Pen(self.default_border_color, self.default_border_width))
        self._penColorDialog.currentColorChanged.connect(self.set_default_border_color)
        self._fillColorDialog.currentColorChanged.connect(self.set_default_fill_color)

    def __setstate__(self, data):
        self.__init__()
        for text in data['texts']:
            text.setParentItem(self)
        self._cornerRadius = data['corner radius']
        self.setPos(data['pos'])
        Connectable._setState(self, data['connectable'])
        Container._setState(self, data['container'])
        
    def __getstate__(self):
        return {
            'texts' : [x for x in self.childItems() if isinstance(x, Text)],
            'corner radius' : self._cornerRadius,
            'pos' : self.pos(),
            'connectable' : Connectable._getState(self, {}),
            'container' : Container._getState(self, {}),
        }
    
    def paint(self, painter:QPainter, option, widget):
        super().paint(painter, option, widget)
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.setRenderHints(self.render_hints)
        painter.drawPath(self._paintPath)
           
    def sceneEventFilter(self, watched, event):
        self._sceneEventFilter(watched, event)
        return super().sceneEventFilter(watched, event)        
    
    def _updatePaintPath(self):
        self._paintPath.clear()
        r = self._cornerRadius
        self._paintPath.addRoundedRect(self.shape_box(), r, r)

    def _updateSelectionPath(self):
        p = self._bboxPad/2.0
        r = self._cornerRadius
        self._selectionPath.clear()
        self._selectionPath.addRoundedRect(self.shape_box().adjusted(-p, -p, p, p), r, r)
    
    def shape_box(self):
        num_attached = self.num_attached_children()
        if num_attached == 0:
            return self.minimum_bbox 
        return super().shape_box()    
    
    def num_attached_children(self):
        count = 0
        for child in self.childItems():
            if child.contained_in_bbox:
                count += 1
        return count
    
    def _updateBoundingBox(self):
        bbox = self.childrenBoundingRect()       
        if self.num_attached_children() == 0:
            bbox = bbox.united(self.minimum_bbox)        
        p = self._bboxPad + self._contentPad
        self._bbox = bbox.adjusted(-p, -p, p, p)
        self.setTransformOriginPoint(self._bbox.width()/2, self._bbox.height()/2)

    @property
    def minimum_bbox(self):
        r = self._cornerRadius
        return QRectF(-r,-r, 2*r, 2*r)
    
    def update(self):       
        self.prepareGeometryChange()
        self._updateBoundingBox()
        self.bbox_collision_response()        
        self._updatePaintPath()
        self._updateSelectionPath()
        if not self.scene() or len(self.scene().items_being_moved) <= 1:
            self.update_connectors()
        super().update()
        if self.parentItem():
            self.parentItem().update()
            
    def itemChange(self, change, value):              
        value = Connectable._itemChange(self, change, value)
        value = Containable._itemChange(self, change, value)
        value = CollisionResponsive._itemChange(self, change, value)       
        
        if self.parentItem():
            self.parentItem().update()
        if change == self.ItemPositionChange:
            self.update_connectors()        
                      
        return super().itemChange(change, value)  
            
    def build_context_menu(self, menu=None):
        if menu is None:
            menu = QMenu()        
        GraphicsShape.build_context_menu(self, menu)
        ColorFillable.build_context_menu(self, menu)
        Containable.build_context_menu(self, menu)
        Snappable.build_context_menu(self, menu)
        Deletable.build_context_menu(self, menu)       
        return menu        

    @staticmethod
    def set_default_border_color(color):
        Object.default_border_color = color
        
    @staticmethod
    def set_default_fill_color(color):
        Object.default_fill_color = color
        
    def closest_boundary_pos_to(self, item):
        radius0 = self._cornerRadius
        if isinstance(item, Object):
            radius1 = item._cornerRadius
        else:
            radius1 = 0
        return self._closest_boundary_pos_to(item, rad0=radius0, rad1=radius1)
    
    def mouseReleaseEvent(self, event):
        Snappable._mouseReleaseEvent(self, event)
        super().mouseMoveEvent(event)
    
    def setPos(self, pos:QPointF, snap:bool=False):
        if snap:
            pos = self.snap_to_grid_pos(pos)
        super().setPos(pos)
        
    #def sceneEventFilter(self, watched, event):
        ##if isinstance(watched, Text):
            ##if event.type() == QEvent.GraphicsSceneMouseMove:
                ##delta = event.pos() - event.lastPos()
                ##self.setPos(self.pos() + delta)
                ##return True
            ##elif event.type() == QEvent.GraphicsSceneMouseRelease:
                ##parent = self.parentItem()
                ##if parent:
                    ##pos = parent.mapFromItem(self, event.pos())
                ##else:
                    ##pos = self.mapToScene(event.pos())
                ##self.setPos(pos, snap=True)
                ##return True
        #return super().sceneEventFilter(watched, event)